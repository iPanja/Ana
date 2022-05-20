import discord
from discord.ext import commands

def setup(bot):
    try:
        bot.add_cog(Moderation(bot))
        print("[Moderation Module Loaded]")
    except Exception as e:
        print(" >> Moderation Module: {0}".format(e))

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.bot.config
        self.word_blacklist = self.config['Moderation']['blacklist']
        self.auto_response = self.config['Moderation']['image_replies']
    
    # Helper method: checks if a word is in the config's blacklist
    def isBlacklisted(self, message):
        for word in self.word_blacklist:
            if word.lower() in message.content.lower():
                return True
        return False
    # Helper method: checks if a message contains a certain word that should be responded with an image
    def getAutoResponse(self, message: str) -> discord.File:
        message = message.lower()
        for word in self.auto_response:
            if word.lower() in message:
                filename = f"files/{self.config['Moderation']['image_replies'][word.lower()]}"
                return discord.File(open(filename, "rb"), filename=filename)
        return None

    
    # Example command: deletes last 50 -> 150 messages in a text channel
    @commands.command(pass_context = True)
    @commands.cooldown(1, 10, commands.BucketType.user) #Can be used 1 time per 10 seconds by each user
    async def clean(self, ctx: commands.Context, max_messages: int = 50):
        if(max_messages >= 150):
            await ctx.channel.send("You can only delete up to 150 messages at a time")
            return
        
        async for x in ctx.channel.history(limit=max_messages):
            await x.delete()
        
        #await ctx.channel.send(f"=== Deleted {max_messages} messages ===")
    
    # Troll command, does nothing
    @commands.command()
    async def monitor(self, ctx: commands.Context, user: discord.Member):
        if(user.id != self.bot.user.id):
            await ctx.send(f"Now monitoring <@{user.id}>")
        else:
            await ctx.send(f"Nice try, <@{ctx.author.id}>")


    # Called on every message sent (by main.py)
    # Will delete messages containing words in the config's blacklist
    async def handle(self, message: discord.Message):
        isBlocked = self.isBlacklisted(message)
        if (isBlocked):
            await message.delete()
            await message.channel.send(self.config["Moderation"]["warning"].format(user=f"<@{message.author.id}>"))
        file = self.getAutoResponse(message.content)
        if not file is None:
            await message.reply(files=[file], content='...')
        """
        if 'daddy' in message.content:
            file = discord.File(filename='files/angry.jpg', fp = open('files/angry.jpg', 'rb'))
            await message.reply(content="...", files=[file])
            """