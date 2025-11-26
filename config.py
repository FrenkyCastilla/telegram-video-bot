"""
Configuration module for Telegram Video Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot configuration class"""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # API Keys
    FIREWORKS_API_KEY = os.getenv('FIREWORKS_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Target Thread ID (optional)
    TARGET_THREAD_ID = os.getenv('TARGET_THREAD_ID')
    if TARGET_THREAD_ID:
        TARGET_THREAD_ID = int(TARGET_THREAD_ID)
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File paths
    TEMP_DIR = 'temp'
    
    # API Endpoints
    FIREWORKS_API_URL = 'https://api.fireworks.ai/inference/v1/audio/transcriptions'
    
    # Model settings
    WHISPER_MODEL = 'whisper-v3'
    GPT_MODEL = 'gpt-4.1-nano'
    
    # System prompt for GPT
    SYSTEM_PROMPT = """Ты — помощник, который создает краткое, структурированное саммари по встрече. 
Используй Markdown, выделяй основные пункты и решения.
Структура ответа должна включать:
- Основные обсуждаемые темы
- Принятые решения
- Следующие шаги
- Назначенные задачи и исполнителей, если они есть

Ответ должен быть не длиннее 500-1000 слов."""
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = {
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'FIREWORKS_API_KEY': cls.FIREWORKS_API_KEY,
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
