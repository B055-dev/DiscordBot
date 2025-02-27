# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import functools
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import discord
from discord.ext import commands

logger = logging.getLogger("Helpers")

def create_embed(
    title: str = None,
    description: str = None,
    color: discord.Color = discord.Color.blue(),
    fields: List[Dict[str, Any]] = None,
    thumbnail: str = None,
    image: str = None,
    author: Dict[str, Any] = None,
    footer: Dict[str, Any] = None,
    timestamp: datetime = None
) -> discord.Embed:
    """Create a Discord embed with the given parameters."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=timestamp or datetime.now()
    )
    
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", ""),
                value=field.get("value", ""),
                inline=field.get("inline", True)
            )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if image:
        embed.set_image(url=image)
    
    if author:
        embed.set_author(
            name=author.get("name", ""),
            url=author.get("url", discord.Embed.Empty),
            icon_url=author.get("icon_url", discord.Embed.Empty)
        )
    
    if footer:
        embed.set_footer(
            text=footer.get("text", ""),
            icon_url=footer.get("icon_url", discord.Embed.Empty)
        )
    
    return embed

def error_embed(title: str, description: str) -> discord.Embed:
    """Create an error embed."""
    return create_embed(
        title=title,
        description=description,
        color=discord.Color.red()
    )

def success_embed(title: str, description: str) -> discord.Embed:
    """Create a success embed."""
    return create_embed(
        title=title,
        description=description,
        color=discord.Color.green()
    )

def warning_embed(title: str, description: str) -> discord.Embed:
    """Create a warning embed."""
    return create_embed(
        title=title,
        description=description,
        color=discord.Color.gold()
    )

def info_embed(title: str, description: str) -> discord.Embed:
    """Create an info embed."""
    return create_embed(
        title=title,
        description=description,
        color=discord.Color.blue()
    )

def format_timedelta(delta: timedelta) -> str:
    """Format a timedelta into a human-readable string."""
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} {'day' if days == 1 else 'days'}")
    if hours > 0:
        parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
    if minutes > 0:
        parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")
    
    return ", ".join(parts)

def is_owner():
    """Check if the user is the bot owner."""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return ctx.author.id in ctx.bot.owner_ids
    return commands.check(predicate)

def is_admin():
    """Check if the user is an admin."""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return ctx.author.guild_permissions.administrator or ctx.author.id in ctx.bot.owner_ids
    return commands.check(predicate)

def is_moderator():
    """Check if the user is a moderator."""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return (
            ctx.author.guild_permissions.manage_messages or
            ctx.author.guild_permissions.administrator or
            ctx.author.id in ctx.bot.owner_ids
        )
    return commands.check(predicate)
 
