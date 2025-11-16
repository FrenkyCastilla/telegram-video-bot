"""
Telegram bot message handlers
"""
import os
import time
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config import Config
from logger import setup_logger
from utils import (
    ensure_temp_dir,
    convert_to_mp3,
    cleanup_file,
    get_file_extension,
    needs_conversion
)
from api_client import transcribe_audio, generate_summary

logger = setup_logger(__name__)
router = Router()

# Store last transcription for /summary command
last_transcription = {}


async def process_video_file(message: Message, file_path: str, file_name: str) -> None:
    """
    Process video/audio file: convert, transcribe, generate summary
    
    Args:
        message: Telegram message object
        file_path: Path to downloaded file
        file_name: Original file name
    """
    start_time = time.time()
    mp3_path = None
    
    try:
        # Check if conversion is needed
        file_ext = get_file_extension(file_name)
        logger.info(f"Processing file: {file_name} (extension: {file_ext})")
        
        if needs_conversion(file_ext):
            # Convert to MP3
            mp3_path = os.path.join(Config.TEMP_DIR, f"{int(time.time())}.mp3")
            
            await message.reply("🔄 Конвертирую файл в MP3...")
            conversion_success = await convert_to_mp3(file_path, mp3_path)
            
            if not conversion_success:
                await message.reply("❌ Ошибка при конвертации файла. Попробуйте другой формат.")
                return
            
            audio_path = mp3_path
        else:
            audio_path = file_path
        
        # Transcribe audio
        await message.reply("🎤 Транскрибирую аудио...")
        transcription = await transcribe_audio(audio_path)
        
        if not transcription:
            await message.reply("❌ Ошибка при транскрибации аудио. Попробуйте позже.")
            return
        
        logger.info(f"Transcription completed: {len(transcription)} characters")
        
        # Store transcription for /summary command
        chat_id = message.chat.id
        thread_id = message.message_thread_id
        key = f"{chat_id}_{thread_id}" if thread_id else str(chat_id)
        last_transcription[key] = transcription
        
        # Generate summary
        await message.reply("📝 Генерирую саммари...")
        summary = await generate_summary(transcription)
        
        if not summary:
            await message.reply("❌ Ошибка при генерации саммари. Попробуйте позже.")
            return
        
        # Format and send response
        response = f"📋 **Итог встречи**\n\n{summary}\n\n_Сгенерировано GPT-ассистентом_"
        
        await message.reply(response, parse_mode="Markdown")
        
        # Log processing time
        elapsed_time = time.time() - start_time
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        await message.reply("❌ Произошла ошибка при обработке файла.")
    
    finally:
        # Cleanup temporary files
        cleanup_file(file_path)
        if mp3_path:
            cleanup_file(mp3_path)


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    welcome_text = """
👋 Привет! Я бот для обработки видео встреч.

**Как использовать:**
1. Отправьте мне видеофайл (.webm, .mp4 и др.) или аудиофайл
2. Я конвертирую его в MP3 (если нужно)
3. Транскрибирую речь
4. Создам краткое саммари встречи

**Команды:**
/summary - Повторно сгенерировать саммари по последней транскрибации
/help - Показать эту справку
    """
    await message.reply(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    await cmd_start(message)


@router.message(Command("summary"))
async def cmd_summary(message: Message):
    """Handle /summary command - regenerate summary from last transcription"""
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    key = f"{chat_id}_{thread_id}" if thread_id else str(chat_id)
    
    if key not in last_transcription:
        await message.reply("❌ Нет доступной транскрибации. Сначала отправьте видео/аудио файл.")
        return
    
    try:
        transcription = last_transcription[key]
        
        await message.reply("📝 Генерирую новое саммари...")
        summary = await generate_summary(transcription)
        
        if not summary:
            await message.reply("❌ Ошибка при генерации саммари. Попробуйте позже.")
            return
        
        response = f"📋 **Итог встречи**\n\n{summary}\n\n_Сгенерировано GPT-ассистентом_"
        await message.reply(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error regenerating summary: {str(e)}", exc_info=True)
        await message.reply("❌ Произошла ошибка при генерации саммари.")


@router.message(F.video | F.document | F.audio | F.voice)
async def handle_media(message: Message):
    """Handle video, document, audio, and voice messages"""
    
    # Check if we should process this message (thread filtering)
    if Config.TARGET_THREAD_ID:
        if message.message_thread_id != Config.TARGET_THREAD_ID:
            logger.debug(f"Ignoring message from thread {message.message_thread_id}")
            return
    
    # Ensure temp directory exists
    ensure_temp_dir(Config.TEMP_DIR)
    
    # Get file info
    file = None
    file_name = None
    
    if message.video:
        file = message.video
        file_name = file.file_name or f"video_{file.file_id}.webm"
    elif message.document:
        file = message.document
        file_name = file.file_name or f"document_{file.file_id}"
    elif message.audio:
        file = message.audio
        file_name = file.file_name or f"audio_{file.file_id}.mp3"
    elif message.voice:
        file = message.voice
        file_name = f"voice_{file.file_id}.ogg"
    
    if not file:
        return
    
    logger.info(f"Received file: {file_name} from user {message.from_user.id}")
    
    try:
        # Download file
        await message.reply("⬇️ Скачиваю файл...")
        
        file_path = os.path.join(Config.TEMP_DIR, f"{int(time.time())}_{file_name}")
        await message.bot.download(file, destination=file_path)
        
        logger.info(f"File downloaded: {file_path}")
        
        # Process the file
        await process_video_file(message, file_path, file_name)
        
    except Exception as e:
        logger.error(f"Error handling media: {str(e)}", exc_info=True)
        await message.reply("❌ Ошибка при обработке файла.")
