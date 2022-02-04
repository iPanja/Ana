import discord, random, difflib, requests, os
from discord.ext import commands
from discord.ext.commands import group

def setup(bot):
    try:
        bot.add_cog(Soundboard(bot))
        print("[Soundboard Module Loaded]")
    except Exception as e:
        print(" >> Soundboard Module: {0}".format(e))

class Soundboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.bot.config
    
    @commands.group()
    async def soundboard(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command, usage:\n  *`ana soundboard add <name>`\n  *`ana soundboard play <name>`\n  *`ana soundboard list`\n  *`ana soundboard delete <name>`')
    
    @soundboard.group(aliases=['new'])
    async def add(self, ctx: commands.Context):
        #ana soundboard add <name ...>
        # Get name
        index = self.bot.command_prefix.count(' ') + 2 # Get location of where <name...> begins
        name = '_'.join(ctx.message.content.lower().split(' ')[index::]) #Get name
        if len(ctx.message.attachments) == 0:
            await ctx.send('Please attach a file to the same message')
            return
        a: discord.Attachment
        for a in ctx.message.attachments:
            #Save
            ext: str = a.filename.split('.')[-1]
            if not ext in self.config['Music']['safe_extensions']:
                await ctx.send(f"**That file extension is not supported, please whitelist it in the config!**")
                return
            filename = name + '.' + ext
            await a.save('files/' + filename)
            await ctx.send(f"Saved audio as {filename}, use `ana soundboard play {filename}` to play it.")

    @soundboard.group()
    async def play(self, ctx: commands.Context):
        # Get file name
        index = self.bot.command_prefix.count(' ') + 2 # Get location of where <name...> begins
        name = '_'.join(ctx.message.content.lower().split(' ')[index::]) #Get name
        # Attempt to play file
        await ctx.invoke(self.bot.get_command('connect'))
        #Prepend a '.' to indicate its a local file rather than a YT video id
        await ctx.invoke(self.bot.get_command('play_local'), filename=f".{name}")
    
    @soundboard.group()
    async def list(self, ctx: commands.Context):
        msg = "**Soundboard sounds:**\nUsage: `ana soundboard play <filename>`\n"
        for filename in os.listdir('files/'):
            msg += f" *{filename}\n"
        await ctx.send(msg)
    
    @soundboard.group()
    async def delete(self, ctx: commands.Context):
        # Get file name
        index = self.bot.command_prefix.count(' ') + 2 # Get location of where <name...> begins
        filename = '_'.join(ctx.message.content.lower().split(' ')[index::]) #Get name
        #Attempt to delete file
        try:
            os.remove('files/' + filename)
        except FileNotFoundError as e:
            await ctx.send('Audio file not found!')
            return
        await ctx.send('Audio file deleted!')