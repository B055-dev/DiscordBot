# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import asyncio
import os
import sys
from pathlib import Path

# Ensure proper directory structure for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import B055Bot
from src.utils.config import Config
from src.utils.logger import setup_logging

async def main():
    # Set up configuration
    config = Config()
    
    # Set up logging
    log_level = config.get("log_level", "INFO")
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "bot.log")
    logger = setup_logging(log_level=log_level, log_file=log_file)
    
    # Create and start the bot
    bot = B055Bot(config=config)
    
    # Get token from config or environment variable
    token = config.get("token") or os.environ.get("BOT_TOKEN")
    
    if not token:
        logger.error("No bot token provided. Set it in config.json or as BOT_TOKEN environment variable.")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        logger.exception(f"Error starting bot: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
 
