import os
import discord
from discord.ext import commands
from asyncio import sleep
import sqlite3
import aiohttp
# from web_server import online

def get_prefix(client, message):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    prefix = cursor.execute(f"SELECT prefix FROM main WHERE guild_id = {message.guild.id}").fetchone()
    cursor.close()
    if prefix:
        return prefix
    return '.'


def get_num_members():
    total = 0
    for guild in client.guilds:
        total += len(guild.members)

    return total


intents = discord.Intents.all()
client = commands.AutoShardedBot(command_prefix=get_prefix,
                                 intents=intents,
                                 help_command=None,
                                 case_insensitive=True,
                      )


# @client.event
# async def on_guild_join(guild):
#     db[guild.id] = '.'


@client.event
async def on_guild_remove(guild):
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM main WHERE guild_id = {guild.id}")
    db.commit()
    cursor.close()


@client.command(aliases=['prefix', 'symbol'])
async def changeprefix(ctx, prefix):
    """``prefix [symbol]`` changes server's prefix"""
    db = sqlite3.connect("main.sqlite")
    cursor = db.cursor()
    if prefix == '.':
        cursor.execute(f"DELETE FROM main WHERE guild_id = {ctx.guild.id}")
    else:
        sql = (f"INSERT INTO main(guild_id, prefix) VALUES(?,?)")
        val = (ctx.guild.id, prefix)
        cursor.execute(sql, val)
    db.commit()
    cursor.close()
    await ctx.send(f"> `server prefix was changed to: {prefix} `")


@client.event
async def on_command_error(ctx, error):
    print(error)


async def status_task():
    while True:
        await client.change_presence(activity=discord.Activity(
            type=0, name=f"in {len(client.guilds)} Servers"))
        await sleep(30)
        await client.change_presence(activity=discord.Activity(
            type=0, name=f"with {len(set(client.get_all_members()))} Users"))
        await sleep(30)


@client.event
async def on_ready():
    client.aioSession = aiohttp.ClientSession()
    client.loop.create_task(status_task())
    print('We have logged in as {0.user}'.format(client))
    

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

if __name__ == "__main__":
    # online()
    client.run(os.environ.get('TOKEN'))
