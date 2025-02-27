# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from src.module_base import ModuleBase

class TestCommandsModule(ModuleBase):
    """Module for testing various slash command features"""

    def __init__(self, bot):
        self.bot = bot  # Make sure to set self.bot before super().__init__
        super().__init__(bot)
        self.color = discord.Color.blue()
        print(f"TestCommandsModule initialized with {len(self.get_commands())} commands")  # Debug print

    @property
    def id(self) -> str:
        return "test_commands"

    @property
    def name(self) -> str:
        return "Test Commands"

    @property
    def description(self) -> str:
        return "Various test commands to demonstrate slash command functionality"

    @property
    def emoji(self) -> str:
        return "🧪"

    def get_commands(self):
        return [
            cmd for cmd in self.__cog_app_commands__
            if isinstance(cmd, app_commands.Command)
        ]

    @app_commands.command()
    async def test(self, interaction: discord.Interaction):
        """A simple test command."""
        await interaction.response.send_message("Test command works!")

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """Sync all slash commands."""
        try:
            if self.bot.default_guild_id:
                guild = discord.Object(id=self.bot.default_guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
            else:
                synced = await self.bot.tree.sync()
            
            await ctx.send(f"Synced {len(synced)} commands!")
            for cmd in synced:
                await ctx.send(f"- /{cmd.name}")
        except Exception as e:
            await ctx.send(f"Failed to sync commands: {e}")

    @app_commands.command(
        name="ping",
        description="Basic ping command to test bot response"
    )
    async def ping(self, interaction: discord.Interaction):
        """Simple ping command."""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"🏓 Pong! Latency: {latency}ms"
        )

    @app_commands.command(
        name="echo",
        description="Repeats your message with optional formatting"
    )
    @app_commands.describe(
        message="The message to repeat",
        style="How to style the message",
        ephemeral="Whether to make the response visible only to you"
    )
    async def echo(
        self,
        interaction: discord.Interaction,
        message: str,
        style: Literal["normal", "bold", "italic", "code"] = "normal",
        ephemeral: bool = False
    ):
        """Echoes back the user's message with optional styling."""
        if style == "bold":
            formatted = f"**{message}**"
        elif style == "italic":
            formatted = f"*{message}*"
        elif style == "code":
            formatted = f"`{message}`"
        else:
            formatted = message

        await interaction.response.send_message(
            formatted,
            ephemeral=ephemeral
        )

    @app_commands.command(
        name="embed",
        description="Creates a test embed with the provided information"
    )
    @app_commands.describe(
        title="The embed title",
        description="The embed description",
        color="The color of the embed"
    )
    async def embed(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: Literal["red", "blue", "green", "gold"] = "blue"
    ):
        """Creates a test embed with user-provided content."""
        color_map = {
            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "gold": discord.Color.gold()
        }

        embed = discord.Embed(
            title=title,
            description=description,
            color=color_map[color]
        )
        
        embed.add_field(
            name="Requested by",
            value=interaction.user.mention,
            inline=True
        )
        embed.add_field(
            name="Channel",
            value=interaction.channel.mention,
            inline=True
        )
        embed.set_footer(
            text=f"Test Embed • Color: {color}"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="button",
        description="Creates a message with interactive buttons"
    )
    async def button(self, interaction: discord.Interaction):
        """Creates a message with interactive buttons."""
        # Create the view with buttons
        view = discord.ui.View(timeout=60)
        
        # Success button
        async def success_callback(button_interaction: discord.Interaction):
            await button_interaction.response.send_message(
                "✅ Success button clicked!",
                ephemeral=True
            )
        
        success_button = discord.ui.Button(
            label="Success",
            style=discord.ButtonStyle.green,
            emoji="✅"
        )
        success_button.callback = success_callback
        view.add_item(success_button)
        
        # Danger button
        async def danger_callback(button_interaction: discord.Interaction):
            await button_interaction.response.send_message(
                "⚠️ Danger button clicked!",
                ephemeral=True
            )
        
        danger_button = discord.ui.Button(
            label="Danger",
            style=discord.ButtonStyle.red,
            emoji="⚠️"
        )
        danger_button.callback = danger_callback
        view.add_item(danger_button)

        await interaction.response.send_message(
            "Test these buttons:",
            view=view
        )

    @app_commands.command(
        name="modal",
        description="Opens a test modal form"
    )
    async def modal(self, interaction: discord.Interaction):
        """Opens a modal form for testing."""
        
        class TestModal(discord.ui.Modal, title="Test Modal"):
            name = discord.ui.TextInput(
                label="Name",
                placeholder="Enter your name",
                required=True,
                max_length=50
            )
            
            feedback = discord.ui.TextInput(
                label="Feedback",
                placeholder="Enter your feedback",
                required=True,
                style=discord.TextStyle.paragraph,
                max_length=500
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                embed = discord.Embed(
                    title="Modal Submission",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Name",
                    value=self.name.value,
                    inline=False
                )
                embed.add_field(
                    name="Feedback",
                    value=self.feedback.value,
                    inline=False
                )
                await modal_interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )

        modal = TestModal()
        await interaction.response.send_modal(modal)

async def setup(bot):
    """Setup function for the test commands module."""
    module = TestCommandsModule(bot)
    await bot.add_module(module)
    print(f"Test commands module setup complete. Commands: {[cmd.name for cmd in module.get_commands()]}")  # Debug print
