# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import asyncio
import logging
import os
import platform
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import discord
import psutil
from discord.ext import commands

from src.module_base import ModuleBase
from src.utils.helpers import create_embed, error_embed, is_admin, is_owner, success_embed

logger = logging.getLogger("AdminModule")

class Admin(ModuleBase):
    """Admin module for bot management."""
    
    @property
    def id(self) -> str:
        return "admin"
    
    @property
    def name(self) -> str:
        return "Admin"
    
    @property
    def description(self) -> str:
        return "Administrative commands for bot management."
    
    @property
    def emoji(self) -> str:
        return "⚙️"
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check the bot's latency."""
        start_time = time.time()
        message = await ctx.send("Pinging...")
        end_time = time.time()
        
        api_latency = round(self.bot.latency * 1000)
        bot_latency = round((end_time - start_time) * 1000)
        
        embed = create_embed(
            title="🏓 Pong!",
            fields=[
                {"name": "API Latency", "value": f"{api_latency}ms", "inline": True},
                {"name": "Bot Latency", "value": f"{bot_latency}ms", "inline": True}
            ],
            color=discord.Color.green()
        )
        
        await message.edit(content=None, embed=embed)
    
    @commands.command(name="stats")
    async def stats(self, ctx):
        """Show bot statistics."""
        # Get system info
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024**2  # Convert to MB
        cpu_usage = psutil.cpu_percent()
        
        # Calculate uptime
        uptime = datetime.now() - datetime.fromtimestamp(process.create_time())
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        
        # Create embed
        embed = create_embed(
            title="Bot Statistics",
            thumbnail=self.bot.user.display_avatar.url,
            fields=[
                {"name": "Bot Version", "value": self.bot.version, "inline": True},
                {"name": "Python Version", "value": platform.python_version(), "inline": True},
                {"name": "Discord.py Version", "value": discord.__version__, "inline": True},
                {"name": "Uptime", "value": uptime_str, "inline": True},
                {"name": "Memory Usage", "value": f"{memory_usage:.2f} MB", "inline": True},
                {"name": "CPU Usage", "value": f"{cpu_usage}%", "inline": True},
                {"name": "Servers", "value": str(len(self.bot.guilds)), "inline": True},
                {"name": "Users", "value": str(len(set(self.bot.get_all_members()))), "inline": True},
                {"name": "Commands", "value": str(len(self.bot.commands)), "inline": True}
            ],
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="reload")
    @is_owner()
    async def reload(self, ctx, module_name: str = None):
        """Reload a module or all modules."""
        if module_name:
            # Reload a specific module
            if module_name not in self.bot.modules:
                await ctx.send(embed=error_embed("Error", f"Module `{module_name}` not found."))
                return
            
            try:
                # Get the module file path
                module_path = f"src.modules.{module_name}"
                
                # Reload the module
                await self.bot.reload_extension(module_path)
                await ctx.send(embed=success_embed("Success", f"Module `{module_name}` reloaded."))
            except Exception as e:
                logger.error(f"Error reloading module {module_name}: {e}")
                await ctx.send(embed=error_embed("Error", f"Failed to reload module `{module_name}`: {e}"))
        else:
            # Reload all modules
            success_count = 0
            error_count = 0
            
            for module_id in list(self.bot.modules.keys()):
                try:
                    module_path = f"src.modules.{module_id}"
                    await self.bot.reload_extension(module_path)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error reloading module {module_id}: {e}")
                    error_count += 1
            
            await ctx.send(embed=success_embed(
                "Reload Complete",
                f"Successfully reloaded {success_count} modules. {error_count} modules failed to reload."
            ))
    
    @commands.command(name="shutdown")
    @is_owner()
    async def shutdown(self, ctx):
        """Shut down the bot."""
        embed = create_embed(
            title="Shutting Down",
            description="The bot is shutting down...",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
        # Close the bot
        await self.bot.close()
    
    @commands.command(name="eval")
    @is_owner()
    async def eval_command(self, ctx, *, code):
        """Evaluate Python code."""
        # This is a dangerous command that should only be used by the bot owner
        try:
            # Add imports that might be useful
            import asyncio
            import discord
            from discord.ext import commands
            
            # Create a local environment with useful variables
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
                'discord': discord,
                'commands': commands,
                'asyncio': asyncio
            }
            
            # Execute the code
            exec(f"async def func():\n{' '*4}{code.replace(chr(10), chr(10)+' '*4)}", env)
            result = await env['func']()
            
            # Send the result
            if result is not None:
                await ctx.send(f"```py\n{result}\n```")
            else:
                await ctx.message.add_reaction('✅')
        except Exception as e:
            await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
            await ctx.message.add_reaction('❌')

async def setup(bot):
    """Set up the Admin module."""
    await bot.add_module(Admin(bot))

 
