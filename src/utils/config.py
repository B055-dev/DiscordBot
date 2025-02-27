# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("Config")

class Config:
    """Configuration manager for the bot."""
    
    def __init__(self, config_path: str = None):
        """Initialize the configuration manager."""
        if config_path is None:
            # Default config path is in the config directory
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "config",
                "config.json"
            )
        else:
            self.config_path = config_path
        
        # Load the configuration file
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from the file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found at {self.config_path}. Creating default config.")
                # Create default config
                default_config = {
                    "token": "",
                    "prefix": "!",
                    "owner_ids": [],
                    "log_level": "INFO",
                    "modules": {
                        "enabled": ["admin"],
                        "disabled": []
                    }
                }
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """Save the configuration to the file."""
        if config_data is None:
            config_data = self.config_data
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split(".")
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        keys = key.split(".")
        config = self.config_data
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated configuration
        return self._save_config()
    
    def reload(self) -> bool:
        """Reload the configuration from the file."""
        try:
            self.config_data = self._load_config()
            return True
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
            return False
 
