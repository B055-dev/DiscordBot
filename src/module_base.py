# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import logging
from abc import abstractmethod
from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("ModuleBase")

class ModuleBase(commands.Cog):
    """Base class for all bot modules."""
    
    def __init__(self, bot):
        """Initialize the module."""
        super().__init__()
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

    async def cog_load(self):
        """Called when the module is loaded."""
        logger.info(f"Module loaded: {self.id} ({self.name})")
    
    async def cog_unload(self):
        """Called when the module is unloaded."""
        logger.info(f"Module unloaded: {self.id} ({self.name})")
