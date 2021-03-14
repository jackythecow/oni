from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
    async def help(self, ctx):
        pass

def setup(client):
    client.add_cog(Help(client))
