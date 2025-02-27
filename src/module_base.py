# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import logging
from abc import abstractmethod
from typing import List, Optional

import discord
from discord.ext import commands

logger = logging.getLogger("ModuleBase")

class ModuleBase(commands.Cog):
    """Base class for all bot modules."""
    
    def __init__(self, bot):
        """Initialize the module."""
        self.bot = bot
        logger.info(f"Initializing module: {self.id} ({self.name})")
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Get the module ID."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the module name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the module description."""
        pass
    
    @property
    def emoji(self) -> str:
        """Get the module emoji."""
        return "🧩"
    
    @property
    def enabled(self) -> bool:
        """Check if the module is enabled."""
        enabled_modules = self.bot.config.get("modules.enabled", [])
        disabled_modules = self.bot.config.get("modules.disabled", [])
        
        if self.id in disabled_modules:
            return False
        
        if not enabled_modules or self.id in enabled_modules:
            return True
        
        return False
    
    async def cog_load(self):
        """Called when the module is loaded."""
        logger.info(f"Module loaded: {self.id} ({self.name})")
    
    async def cog_unload(self):
        """Called when the module is unloaded."""
        logger.info(f"Module unloaded: {self.id} ({self.name})")
    
    async def cog_check(self, ctx):
        """Check if the module is enabled before executing commands."""
        return self.enabled
