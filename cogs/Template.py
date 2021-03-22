from discord.ext import commands


class Template(commands.Cog):
    def __init__(self, client):
        self.client = client

    # @commands.command(hidden=True)
    # async def command(self, ctx):
    #     pass

def setup(client):
    client.add_cog(Template(client))
