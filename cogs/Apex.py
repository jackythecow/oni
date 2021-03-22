from discord.ext import commands
import discord

from aiohttp import request
import os

def nextrank(score):
    #Masters+
    if score >= 10000:
        return "RP"
    #Diamond
    elif score >= 7200:
        return "/"+str(((score - 7200) // 700 + 1) * 700 + 7200)+"RP"
    #Platinum
    elif score >= 4800:
        return "/"+str(((score - 4800) // 600 + 1) * 600 + 4800)+"RP"
    #Gold
    elif score >= 2800:
        return "/"+str(((score - 2800) // 500 + 1) * 500 + 2800)+"RP"
    #Silver
    elif score >= 1200:
        return "/"+str(((score - 1200) // 400 + 1) * 400 + 1200)+"RP"
    #Broze
    else:
        return "/"+str(((score // 300 + 1) * 300))+"RP"

        

class Apex(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def getdata(self, ctx, URL):
        async with request("GET", URL) as response: #, headers={'TRN-Api-Key': os.getenv('APEX')}) as response:
            data = await response.json(content_type='text/plain')
            return data
        

    @commands.command(aliases=["alstats","stat","stats"])
    async def apex_stats(self, ctx, id, platform='PC'):
        """`stats <id>` gets apex stats from origin id"""
        # URL = f"https://public-api.tracker.gg/v2/apex/standard/profile/{platform}/{id}"
        URL = "https://api.mozambiquehe.re/bridge?version=5&platform={}&player={}&auth={}".format(platform, id, os.getenv('APEX')).replace("'","")
        data = await self.getdata(ctx, URL)
        rank = data['global']['rank']
        legend = data['legends']['selected']

        embed=discord.Embed(title="", color=0xcdcfbb)
        embed.set_author(name=f"{data['global']['name']}'s stats", icon_url=f"{data['global']['rank']['rankImg']}")
        embed.set_thumbnail(url=f"{legend['ImgAssets']['icon']}")
        embed.add_field(name="Rank", value=f"`{rank['rankName']} {rank['rankDiv']}`\
        \n`{rank['rankScore']}{nextrank(rank['rankScore'])}`", inline=False)
        embed.add_field(name="Active Legend", value=f"`{legend['LegendName']}`", inline=False)

        for index in range(len(legend['data'])):
            embed.add_field(name=f"{legend['data'][index]['name'].title()}", value=f"`{legend['data'][index]['value']}`", inline=False)
        
        embed.set_footer(text=f"Level {data['global']['level']} ({data['global']['toNextLevelPercent']}%)")
        await ctx.send(embed=embed)

    
def setup(client):
    client.add_cog(Apex(client))
