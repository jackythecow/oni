from discord.ext import commands

import sqlite3


class Message(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.content.startswith('oni.prefix'):
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            prefix = cursor.execute(f"SELECT prefix FROM main WHERE guild_id = {message.guild.id}").fetchone()
            if prefix:
                return await message.channel.send(f"> The prefix for this server is `'{prefix[0]}'`")
            return await message.channel.send("> The prefix for this server is `'.'`")
        
        # if "kys" in message.content:
        #    await message.channel.send('> `HAHA YOU`')



def setup(client):
    client.add_cog(Message(client))
