from discord.ext import commands

import sqlite3

class Osu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["setosu"])
    async def set_osu(self, ctx, username=None):
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

    @commands.command(aliases=["getosu"])
    async def get_osu(self, ctx):
        authorid = ctx.author.id
        try:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"""
            SELECT osu_id FROM osuid WHERE author_id={authorid} 
            """)
            if (cursor != None):
                username = cursor.fetchone()
            await ctx.send(f"> osu! username is set to `{username}`")
        except:
            await ctx.send("> Could not find osu! username")


def setup(client):
    client.add_cog(Osu(client))
