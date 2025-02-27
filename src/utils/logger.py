# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging(log_level="INFO", log_file=None):
    """Set up logging with color support and optional file output."""
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with color formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    console_formatter = ColoredFormatter(console_format, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        file_formatter = logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger
 
