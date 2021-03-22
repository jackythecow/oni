import discord 
from discord.ext import commands

import random

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes, definitely",
                     "You may rely on it", "As I see it, yes", "Most Likely", "Outlook Good",
                     "Yes", "No", "Signs point to yes", "Reply hazy, try again", "Ask again later",
                     "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
                    "Very Doubtful"]
        
    def _get_id_match(self):
        return self._id_regex.match(self.argument)

    @commands.command(aliases=['dice'])
    async def roll(self, ctx, *, integer=6):
        """`roll <int>` rolls random value starting from 1 to [int]"""
        try:
            await ctx.send(
                f"> {ctx.message.author.mention} rolled a `{random.randrange(int(integer))+1}`."
            )
        except:
            await ctx.send("Please enter an integer")

    @commands.command(aliases=['8b', '8ball'])
    async def eightball(self, ctx, *, question):
        """`8ball [question]` gives an answer to a question"""
        
        
        await ctx.send(
            f"```Question: {question}\nAnswer: {random.choice(self.responses)}```")

    @commands.command(aliases=['coin'])
    async def flip(self, ctx):
        """`flip` flips a coin"""
        possible_responses = ["heads", "tails"]
        await ctx.send(f"> {ctx.author.mention} flipped `{random.choice(possible_responses)}`")

    @commands.command(aliases=['pfp'])
    async def profilepicture(self, ctx):
        """`pfp [mentions]` sends mentioned profile picture"""
        for member in ctx.message.mentions:
            await ctx.send(embed=discord.Embed().set_image(
                url=member.avatar_url))

    @commands.command(aliases=['choice'])
    async def choose(self, ctx, *, content: commands.clean_content):
        """`choose [option]|[option]|[option]` Chooses between multiple choices."""
        content = content.split("|")
        await ctx.send(f"> Selected: `{random.choice(content)}`")


def setup(client):
    client.add_cog(Fun(client))
