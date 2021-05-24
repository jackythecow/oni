from discord.ext import commands


class Code(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def run(self, ctx, language, content):
        
        async with self.client.aioSession.post(
            "https://emkc.org/api/v1/piston/execute", 
            data={"language": language,
                  "source": content}
        ) as response:
            r = await response.json()

        output = " " if not r["output"] else r["output"]
        await ctx.send(f"```{output}```", delete_after=180)


    @commands.command(aliases=["py", "py3"])
    async def python3(self, ctx, *, content: commands.clean_content):
        """`py3 [code]` run python3 code"""
        content = content.replace("```", "")
        await self.run(ctx, "python3", content)

    @commands.command(aliases=["j"])
    async def java(self, ctx, *, content: commands.clean_content):
        """`java [code]` run java code"""
        content = content.replace("```", "")
        await self.run(ctx, "java", content)

    @commands.command(aliases=["jf"])
    async def javaf(self, ctx, *, content: commands.clean_content):
        """`javaf [code]` run java code, automatically add class and main"""
        content = """public class X{
            public static void main(String[] args){
                """+content.replace("```", "")+"}}"
        await self.run(ctx, "java", content)

    @commands.command(aliases=["js"])
    async def javascript(self, ctx, *, content: commands.clean_content):
        """`javascript [code]` run java code, automatically add class and main"""
        content = content.replace("```", "")
        await self.run(ctx, "js", content)

    @commands.command()
    async def c(self, ctx, *, content: commands.clean_content):
        """`c [code]` run c code"""
        content = content.replace("```", "")
        await self.run(ctx, "c", content)

    @commands.command(aliases=["c++"])
    async def cpp(self, ctx, *, content: commands.clean_content):
        """`cpp [code]` run cpp code"""
        content = content.replace("```", "")
        await self.run(ctx, "cpp", content)

def setup(client):
    client.add_cog(Code(client))
