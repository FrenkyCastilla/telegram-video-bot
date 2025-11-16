"""
API client for Fireworks Whisper and OpenAI GPT
"""
import aiohttp
import asyncio
from openai import OpenAI
from config import Config
from logger import setup_logger

logger = setup_logger(__name__)

# Initialize OpenAI client
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)


async def transcribe_audio(audio_file_path: str, max_retries: int = 3) -> str | None:
    """
    Transcribe audio file using Fireworks Whisper v3 API
    
    Args:
        audio_file_path: Path to audio file (MP3, WAV, etc.)
        max_retries: Maximum number of retry attempts
        
    Returns:
        Transcribed text or None if failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Transcribing audio (attempt {attempt + 1}/{max_retries}): {audio_file_path}")
            
            async with aiohttp.ClientSession() as session:
                # Prepare multipart form data
                with open(audio_file_path, 'rb') as audio_file:
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', 
                                       audio_file, 
                                       filename=audio_file_path.split('/')[-1],
                                       content_type='audio/mpeg')
                    form_data.add_field('model', Config.WHISPER_MODEL)
                    
                    headers = {
                        'Authorization': f'Bearer {Config.FIREWORKS_API_KEY}'
                    }
                    
                    # Make API request
                    async with session.post(
                        Config.FIREWORKS_API_URL,
                        data=form_data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            transcription = result.get('text', '')
                            
                            if transcription:
                                logger.info(f"Transcription successful: {len(transcription)} characters")
                                return transcription
                            else:
                                logger.warning("Empty transcription received")
                                
                        else:
                            error_text = await response.text()
                            logger.error(f"Fireworks API error (status {response.status}): {error_text}")
            
            # Wait before retry
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout during transcription (attempt {attempt + 1})")
        except Exception as e:
            logger.error(f"Error during transcription (attempt {attempt + 1}): {str(e)}", exc_info=True)
        
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)
    
    logger.error("All transcription attempts failed")
    return None


async def generate_summary(transcription: str, max_retries: int = 3) -> str | None:
    """
    Generate summary from transcription using OpenAI GPT
    
    Args:
        transcription: Transcribed text
        max_retries: Maximum number of retry attempts
        
    Returns:
        Generated summary or None if failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Generating summary (attempt {attempt + 1}/{max_retries})")
            
            # Run OpenAI API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: openai_client.chat.completions.create(
                    model=Config.GPT_MODEL,
                    messages=[
                        {"role": "system", "content": Config.SYSTEM_PROMPT},
                        {"role": "user", "content": f"Создай саммари по следующей транскрибации встречи:\n\n{transcription}"}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
            )
            
            summary = response.choices[0].message.content
            
            if summary:
                logger.info(f"Summary generated: {len(summary)} characters")
                return summary.strip()
            else:
                logger.warning("Empty summary received")
                
        except Exception as e:
            logger.error(f"Error generating summary (attempt {attempt + 1}): {str(e)}", exc_info=True)
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    logger.error("All summary generation attempts failed")
    return None
