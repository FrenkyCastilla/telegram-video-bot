"""
Utility functions for video/audio processing
"""
import os
import ffmpeg
from pathlib import Path
from logger import setup_logger

logger = setup_logger(__name__)


async def convert_to_mp3(input_path: str, output_path: str) -> bool:
    """
    Convert video/audio file to MP3 format using ffmpeg
    
    Args:
        input_path: Path to input file
        output_path: Path to output MP3 file
        
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        logger.info(f"Converting {input_path} to {output_path}")
        
        # Convert using ffmpeg-python
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, acodec='libmp3lame', audio_bitrate='192k')
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        logger.info(f"Conversion successful: {output_path}")
        return True
        
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error during conversion: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")
        return False


def ensure_temp_dir(temp_dir: str) -> None:
    """
    Ensure temporary directory exists
    
    Args:
        temp_dir: Path to temporary directory
    """
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    logger.debug(f"Temporary directory ensured: {temp_dir}")


def cleanup_file(file_path: str) -> None:
    """
    Remove file if it exists
    
    Args:
        file_path: Path to file to remove
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (lowercase, without dot)
    """
    return Path(filename).suffix.lower().lstrip('.')


def needs_conversion(file_extension: str) -> bool:
    """
    Check if file needs conversion to MP3
    
    Args:
        file_extension: File extension (without dot)
        
    Returns:
        True if conversion needed, False otherwise
    """
    # Supported audio formats that don't need conversion
    supported_audio = ['mp3']
    
    # Video formats and other audio formats need conversion
    return file_extension not in supported_audio
