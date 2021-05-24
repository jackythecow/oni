import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.listCogs = ['Apex', 'Code',
                         'Dev', 'Fun',
                         'Help', 'Images',
                         'Management',
                         'Music', #'Osu',
                         'Stocks', 
                         ]

    @commands.command(hidden=True)
    async def help(self, ctx, extension=""):
        """`help <extension>` display commands in extension"""
        extension = extension.capitalize()

        if not extension:
            names = ""
            for name in self.listCogs:
                names += name+"\n"
            embed = discord.Embed(title="Extensions", 
                                  description=names)

        else:
            embed = discord.Embed(title=extension)
            cog = self.client.get_cog(extension)

            commands = cog.get_commands()
            for c in commands:
                embed.add_field(name=c.name,
                                value=c.short_doc,
                                inline=False)

        await ctx.send(embed=embed)

        
def setup(client):
    client.add_cog(Help(client))
