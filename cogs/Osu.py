from discord.ext import commands

import sqlite3
from aiohttp import request

def get_osu_id(ctx):
    authorid = ctx.author.id
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f"""
        SELECT osu_id FROM osuid WHERE author_id={authorid} 
        """)
    if (cursor != None):
        try:
            return cursor.fetchone()[0]
        except:
            return None
    else:
        return None

class Osu(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def getdata(self, ctx, URL):
        async with request(
                "GET", URL
        ) as response:
            data = await response.json(content_type='application/json')
            return data

    @commands.command(aliases=["setosu"])
    async def set_osu(self, ctx, username=None):
        """`setosu [osu_id]` set your osu! id"""
        authorid = ctx.author.id
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        if username != "" and username is not None:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO osuid(author_id, osu_id) VALUES (?,?)
                """,(authorid, username))
                await ctx.send(f"> Successfully set osu! username to `{username}`")
            except:
                await ctx.send(f"> Could not set osu! username to `{username}`")
        else:
            cursor.execute(f"""
                    DELETE FROM osuid WHERE author_id={authorid}
                """)
            await ctx.send("> Removed osu! username, hopefully")
        db.commit()
        db.close()

    @commands.command(aliases=["getosu"])
    async def get_osu(self, ctx):
        """`getosu` get your osu! id"""
        try:
            username = get_osu_id(ctx)
            await ctx.send(f"> osu! username is set to `{username}`")
        except:
            await ctx.send("> Could not find osu! username")

    @commands.command(aliases=["delosu"])
    async def del_osu(self, ctx):
        """`delosu` delete osu! id"""
        authorid = ctx.author.id
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"""
            DELETE FROM osuid WHERE author_id={authorid}
            """)
        db.commit()
        db.close()
        await ctx.send("> Removed osu! username, hopefully")

    @commands.command(aliases=[])
    async def recent(self, ctx):
        """`recent` get recent osu! score `WIP`"""
        try:
            osu_id = get_osu_id(ctx)
            await ctx.send("> `no`")
        except:
            pass


def setup(client):
    client.add_cog(Osu(client))
