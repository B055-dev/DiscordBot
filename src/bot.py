# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import asyncio
import importlib
import inspect
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type

import discord
from discord.ext import commands

from src.module_base import ModuleBase
from src.utils.config import Config

logger = logging.getLogger("Bot")

class B055Bot(commands.Bot):
    """Main bot class for B055."""

    def __init__(self, config: Config):
        """Initialize the bot."""
        self.version = "1.0.0"
        self.config = config
        self.modules: Dict[str, ModuleBase] = {}

        # Get bot settings from config
        prefix = config.get("prefix", "!")
        owner_ids = set(config.get("owner_ids", []))

        # Initialize the bot with intents
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            owner_ids=owner_ids,
            intents=intents,
            case_insensitive=True,
            help_command=None  # We'll implement our own help command
        )

    async def setup_hook(self) -> None:
        """Set up the bot before connecting to Discord."""
        await self.load_modules()

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Set the bot's status and activity
        status_str = self.config.get("status", "online")
        status_map = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        status = status_map.get(status_str, discord.Status.online)

        # Set activity
        activity_type = self.config.get("activity_type", "playing")
        activity_name = self.config.get("activity_name", "with commands")

        activity_map = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
            "streaming": discord.ActivityType.streaming,
            "competing": discord.ActivityType.competing
        }

        if activity_type in activity_map:
            activity = discord.Activity(type=activity_map[activity_type], name=activity_name)
        else:
            activity = discord.Game(name=activity_name)

        await self.change_presence(status=status, activity=activity)

    async def on_message(self, message):
        """Process messages."""
        # Ignore messages from bots
        if message.author.bot:
            return

        # Process commands
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Bad argument: {error}")
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You don't have permission to use this command.")
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"I don't have the necessary permissions to do that.")
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("You don't have permission to use this command.")
            return

        # Log unexpected errors
        logger.error(f"Command error in {ctx.command}: {error}")
        logger.error(traceback.format_exception(type(error), error, error.__traceback__))

        # Notify the user
        await ctx.send(f"An error occurred while executing the command: {error}")

    async def add_module(self, module: ModuleBase) -> None:
        """Add a module to the bot."""
        self.modules[module.id] = module
        await self.add_cog(module)  # Now properly awaited
        logger.info(f"Added module: {module.id} ({module.name})")

    async def load_modules(self) -> None:
        """Load all modules."""
        modules_dir = os.path.join(os.path.dirname(__file__), "modules")
        module_files = [f[:-3] for f in os.listdir(modules_dir) if f.endswith(".py") and not f.startswith("_")]

        # Get enabled and disabled modules from config
        enabled_modules = self.config.get("modules.enabled", [])
        disabled_modules = self.config.get("modules.disabled", [])

        for module_file in module_files:
            # Skip disabled modules
            if module_file in disabled_modules:
                logger.info(f"Skipping disabled module: {module_file}")
                continue

            # Skip modules not in enabled_modules if it's specified
            if enabled_modules and module_file not in enabled_modules:
                logger.info(f"Skipping module not in enabled list: {module_file}")
                continue

            try:
                # Import the module
                module_path = f"src.modules.{module_file}"
                
                # Use load_extension instead of manual import
                await self.load_extension(module_path)
                logger.info(f"Loaded extension: {module_path}")
                
            except Exception as e:
                logger.error(f"Error loading module {module_file}: {e}")
                logger.error(traceback.format_exception(type(e), e, e.__traceback__))
