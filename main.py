import discord, toml, os
from discord.ext import tasks, commands

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix = '!', intents = discord.Intents.default(), config = None, cogs = []):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.config = config
        # Load cogs
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                print('Failed to load module {0}\n{1} : {2}'.format(cog, type(e).__name__, e))
    
    # Event: on_ready
    async def on_ready(self):
        print(f"Loading bot: {self.user.id}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="from your walls"))

    # Event: on_message
    async def on_message(self, message: discord.Message):
        await self.get_cog("Moderation").handle(message) # Send the message to a specific cog to use
        await self.get_cog("Vigil").on_message(message)
        await self.process_commands(message) # Still have discord process the potential command normally
    # Event: on_reaction_add
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        await self.get_cog("Vigil").on_reaction_add(reaction, user)
    # Event: on_message_delete
    async def on_message_delete(self, message: discord.Message):
        await self.get_cog("Vigil").on_message_delete(message)
    # Event: on_message_ban
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        await self.get_cog("Vigil").on_member_ban(guild, member)
    # Event: on member_kick
    async def on_member_kick(self, guild: discord.Guild, member: discord.Member):
        await self.get_cog("Vigil").on_member_kick(guild, member)
        pass

    # Event: on_command_error
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send('This command is on a %.2fs cooldown' % error.retry_after)
            return
        if isinstance(error, commands.CommandNotFound):
            return
        raise error
    
# Debugging
os.chdir("/home/pi/Documents/Ana")

# Load config file
with open('config.toml', 'r') as file:
    data = file.read()
config = toml.loads(data)

# Start bot
intents = discord.Intents.default()
intents.members = True
client = DiscordBot(command_prefix='ana ', intents=intents, config=config, cogs=config['Bot']['cogs'])
client.run(config['Bot']['Token'])