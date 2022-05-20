import discord
from discord.ext import commands
from datetime import datetime

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

    
    # Troll command, does nothing
    @commands.command()
    async def monitor(self, ctx: commands.Context, user: discord.Member):
        if(user.id != self.bot.user.id):
            await ctx.send(f"Now monitoring <@{user.id}>")
        else:
            await ctx.send(f"Nice try, <@{ctx.author.id}>")


    # Events are called by main.py
    async def on_message(self, message: discord.Message):
        pass

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        pass

    async def on_message_delete(self, message: discord.Message):
        print(f"Message deleted: \n{message.content}\n")
    
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        log_entry: discord.AuditLogEntry = await guild.audit_logs().find(predicate=self.predicate_bans)
        author: discord.Member = log_entry.user
        target: discord.User = log_entry.target
        reason: str = log_entry.reason
        time: datetime = log_entry.created_at
        # Create embed
        embed: discord.Embed = discord.Embed(title="A user has been banned", color=discord.Color.purple())
        embed.add_field("Moderator", author)
        embed.add_field("Target", target)
        embed.add_field("Reason", reason)
        embed.add_field("Time", time)
        embed.set_footer(text=self.config['Bot']['embed_footer'])
        guild.text_channels[0].send(content=None, embed=embed)

    async def on_member_kick(self, guild: discord.Guild, member: discord.Member):
        log_entry: discord.AuditLogEntry = await guild.audit_logs().find(predicate=self.predicate_kicks)
        author: discord.Member = log_entry.user
        target: discord.User = log_entry.target
        reason: str = log_entry.reason
        time: datetime = log_entry.created_at
        # Create embed
        embed: discord.Embed = discord.Embed(title="A user has been kicked", color=discord.Color.purple())
        embed.add_field("Moderator", author)
        embed.add_field("Target", target)
        embed.add_field("Reason", reason)
        embed.add_field("Time", time)
        embed.set_footer(text=self.config['Bot']['embed_footer'])
        guild.text_channels[0].send(content=None, embed=embed)
    
    # /// HELPERS
    def predicate_bans(self, event: discord.AuditLogEntry):
        return event.action is discord.AuditLogAction.ban
    def predicate_kicks(self, event: discord.AuditLogEntry):
        return event.action is discord.AuditLogAction.kick