from discord.ext import commands
import discord

from aiohttp import request
import os
import json

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
        with open('data/weapons.txt') as file:
            self.weapon = json.load(file)
        self.color = {
            "Energy":[0x636f1d,"https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/2/2d/Energy_Ammo.svg/revision/latest/scale-to-width-down/256?cb=20190827163648"],
            "Heavy":[0x376654,"https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/55/Heavy_Rounds.svg/revision/latest/scale-to-width-down/254?cb=20190827144859"],
            "Unique":[0xcb003c,"https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/7/7f/Supply_Drop_Sniper_Ammo.svg/revision/latest/scale-to-width-down/273?cb=20200819185728"],
            "Light":[0xf49b49,"https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/a/a5/Light_Rounds.svg/revision/latest/scale-to-width-down/254?cb=20190827144754"],
            "Shotgun":[0x831600,"https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/4/42/Shotgun_Shells.svg/revision/latest/scale-to-width-down/254?cb=20190827163750"],
            "Sniper":[0x7c80fb,"https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/3/3e/Sniper_Ammo.svg/revision/latest/scale-to-width-down/256?cb=20200207225134"]
        }

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

    @commands.command(aliases=['wep','weap'])
    async def weapon(self, ctx, weapon=None):
        """`weapon <weapon>` return weapon stats."""
        if not weapon:
            all=""
            embed=discord.Embed(title="Apex Legends Weapon List", color=0xcdcfbb)
            for category in self.weapon:
                for name in self.weapon[category]:
                    all += self.weapon[category][name]['displayName']+f" `{name}`"+"\n"
                embed.add_field(name=f"{category}", value=f"{all}", inline=False)
                all = ""
            await ctx.send(embed=embed)

        else:
            weapon = weapon.capitalize()
            for category in self.weapon:
                if weapon in self.weapon[category]:
                    type = category
                    data = self.weapon[category][weapon]
                    
                    embed=discord.Embed(title=f"{data['displayName']}", color=self.color[data['ammoType']][0]) #description=f"{data['ammoType']}",)
                    embed.set_author(name=f"{type}", icon_url=self.color[data['ammoType']][1])
                    embed.set_image(url=f"{data['imgUrl']}")
                    embed.add_field(name="Damage", value=f"`{data['damage']}`", inline=False)
                    embed.add_field(name="Magazine Size", value=f"`{data['magSize']}`", inline=True)
                    embed.add_field(name="Reload Speed", value=f"`{data['reload']}`", inline=True)
                    embed.add_field(name="RPM", value=f"`{data['RPM']}`", inline=True)
                    await ctx.send(embed=embed)
                    break;

    
def setup(client):
    client.add_cog(Apex(client))
