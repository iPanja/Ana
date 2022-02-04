from dis import disco
import discord, random, difflib, requests
from discord.ext import commands

def setup(bot):
    try:
        bot.add_cog(Valorant(bot))
        print("[Valorant Module Loaded]")
    except Exception as e:
        print(" >> Valorant Module: {0}".format(e))

class Valorant(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.bot.config
    
    @commands.command()
    async def valagent(self, ctx: commands.Context):
        #await ctx.send(f"Play {random.choice(self.config['Valorant']['agents'])}")
        embed=discord.Embed(title='Valorant Agent Roulette', description=f"You must play {random.choice(self.config['Valorant']['agents'])}", color=discord.Color.red())
        embed.set_footer(text=self.config['Bot']['embed_footer'])
        await ctx.send(content=None, embed=embed)
    
    @commands.command()
    async def valstrat(self, ctx: commands.Context, map:str, side: str):
        maps = ['Bind', 'Breeze', 'Fracture', 'Haven', 'Split', 'Ascent']
        sides = ['atk', 'def', 'any']
        map = difflib.get_close_matches(map, maps)[0].lower()
        side = difflib.get_close_matches(side, sides)[0].lower()
        strat = requests.get(f"https://api.diah.info/valorant/roulette.php?map={map}&side={side}").text
        #await ctx.send(f"Random strat: {response}")
        embed: discord.Embed = discord.Embed(title='Valorant Strat Roulette', description=strat, color=discord.Color.red())
        embed.add_field(name="Source:", value="https://www.diah.info/valorant/roulette/", inline=True)
        embed.set_footer(text=self.config['Bot']['embed_footer'])
        await ctx.send(content=None, embed=embed)
