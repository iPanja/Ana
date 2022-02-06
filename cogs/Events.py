from __future__ import annotations
import discord
from discord.ext import commands
import pafy, urllib, re, enum, random
from typing import List, Union, Set

def setup(bot):
    try:
        bot.add_cog(Music(bot))
        print("[Music* Module Loaded]")
    except Exception as e:
        print(" >> Music* Module: {0}".format(e))
    

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.bot.config
    
    # /// Commands
    @commands.command()
    async def event(self, ctx: commands.Context, *args):
        preset_name = args[0].lower()
        if preset_name in self.get_preset_list():
            # Create category
            guild: discord.Guild = ctx.guild
            preset_config = self.get_preset_config(preset_name)
            category: discord.CategoryChannel = await guild.create_category(preset_config['category'])
            # Create sub-channels
            channel_prefix = '[E] '
            if args[1].isnumeric():
                # User inputted a number, create n channels
                
                for n in range(0, int(args[1])):
                    name = str(n+1)
                    await category.create_voice_channel(channel_prefix + preset_config['channels'].format(name=name))
            else:
                # User is inputting a list of team names?
                for i in range(0, len(args)-1):
                    name = args[i+1].replace('_', ' ') #Team_Obsidian -> Team Obsidian
                    await category.create_voice_channel(channel_prefix + preset_config['channels'].format(name=name))

    @commands.command(aliases=['event_cleanup'])
    async def event_clean(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        categories: list[discord.CategoryChannel] = list()
        # Locate channels and clean them up
        for vc in guild.voice_channels:
            if vc.name.startswith('[E]'):
                if not vc.category is None:
                    categories.append(vc.category)
                await vc.delete()
        # Delete the category as well
        for cg in set(categories):
            await cg.delete()


    # /// Helpers
    def get_preset_list(self):
        return list(self.config['Events'].keys())
    def get_preset_config(self, preset_name: str):
        return self.config['Events'][preset_name]
