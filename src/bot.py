# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import asyncio
import importlib
import inspect
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type, Set

import discord
from discord import app_commands
from discord.ext import commands, tasks

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
        self.last_module_check = 0
        self.loaded_modules: Set[str] = set()

        # Get bot settings from config
        self.default_guild_id = config.get("default_guild_id", None)
        owner_ids = set(config.get("owner_ids", []))

        # Initialize the bot with intents
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            owner_ids=owner_ids,
            intents=intents,
            help_command=None
        )

    async def setup_hook(self) -> None:
        """Set up the bot before connecting to Discord."""
        await self.auto_load_modules()
        self.check_modules.start()  # Start the module checking loop
        
        # Sync commands with Discord
        if self.default_guild_id:
            guild = discord.Object(id=self.default_guild_id)
            self.tree.copy_global_to(guild=guild)
            try:
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} commands to guild {self.default_guild_id}")
                for cmd in synced:
                    logger.info(f"Synced command: /{cmd.name}")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
                logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        else:
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} commands globally")
                for cmd in synced:
                    logger.info(f"Synced command: /{cmd.name}")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")
                logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

    def get_module_files(self) -> Set[str]:
        """Get a set of all valid module files in the modules directory."""
        modules_dir = os.path.join(os.path.dirname(__file__), "modules")
        if not os.path.exists(modules_dir):
            os.makedirs(modules_dir)
            return set()
        
        return {
            f[:-3] for f in os.listdir(modules_dir)
            if f.endswith(".py") and not f.startswith("_")
        }

    @tasks.loop(seconds=5)
    async def check_modules(self):
        """Periodically check for module changes."""
        try:
            current_modules = self.get_module_files()
            
            # Check for new modules to load
            modules_to_load = current_modules - self.loaded_modules
            for module_name in modules_to_load:
                try:
                    module_path = f"src.modules.{module_name}"
                    await self.load_extension(module_path)
                    self.loaded_modules.add(module_name)
                    logger.info(f"Automatically loaded new module: {module_name}")
                except Exception as e:
                    logger.error(f"Error loading new module {module_name}: {str(e)}")
                    logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

            # Check for modules to unload
            modules_to_unload = self.loaded_modules - current_modules
            for module_name in modules_to_unload:
                try:
                    module_path = f"src.modules.{module_name}"
                    await self.unload_extension(module_path)
                    self.loaded_modules.remove(module_name)
                    logger.info(f"Automatically unloaded removed module: {module_name}")
                except Exception as e:
                    logger.error(f"Error unloading module {module_name}: {str(e)}")
                    logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

            # Check for modified modules to reload
            for module_name in current_modules & self.loaded_modules:
                module_path = os.path.join(os.path.dirname(__file__), "modules", f"{module_name}.py")
                if os.path.exists(module_path):
                    mod_time = os.path.getmtime(module_path)
                    if mod_time > self.last_module_check:
                        try:
                            module_path = f"src.modules.{module_name}"
                            await self.reload_extension(module_path)
                            logger.info(f"Automatically reloaded modified module: {module_name}")
                        except Exception as e:
                            logger.error(f"Error reloading module {module_name}: {str(e)}")
                            logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

            self.last_module_check = time.time()

        except Exception as e:
            logger.error(f"Error in module checker: {str(e)}")
            logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

    @check_modules.before_loop
    async def before_check_modules(self):
        """Wait until the bot is ready before starting the module checker."""
        await self.wait_until_ready()

    async def add_module(self, module: ModuleBase) -> None:
        """Add a module to the bot."""
        self.modules[module.id] = module
        await self.add_cog(module)
        logger.info(f"Added module: {module.id} ({module.name})")

    async def auto_load_modules(self) -> None:
        """Automatically load all modules from the modules directory."""
        current_modules = self.get_module_files()
        
        for module_name in current_modules:
            try:
                module_path = f"src.modules.{module_name}"
                await self.load_extension(module_path)
                self.loaded_modules.add(module_name)
                logger.info(f"Loaded module: {module_name}")
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {str(e)}")
                logger.error(''.join(traceback.format_exception(type(e), e, e.__traceback__)))

    async def close(self):
        """Clean up before closing."""
        self.check_modules.cancel()  # Stop the module checker
        await super().close()

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Debug: Print all registered commands
        logger.info("Registered commands:")
        for cmd in self.tree.get_commands():
            logger.info(f"- /{cmd.name}: {cmd.description}")
