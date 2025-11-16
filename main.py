"""
Main entry point for Telegram Video Bot
"""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config
from logger import setup_logger
from handlers import router
from utils import ensure_temp_dir

logger = setup_logger(__name__)


async def main():
    """Main function to run the bot"""
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    # Ensure temp directory exists
    ensure_temp_dir(Config.TEMP_DIR)
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=Config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.include_router(router)
    
    logger.info("Starting bot...")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during polling: {str(e)}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
