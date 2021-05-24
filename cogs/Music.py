import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
import os
from pathlib import Path
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


ytdl_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'restrictfilenames': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'audioformat': 'mp3',
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',    
                  'options': '-vn'
}

ytdl = YoutubeDL(ytdl_options)


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'Added `{data["title"]}` to the Queue', delete_after=20)

        if download:
            source = ytdl.prepare_filename(data)
            source = Path(source).with_suffix(".mp3")
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """makes queues and loops for different guilds"""

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """main player loop"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(600):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                if self in self._cog.players.values():
                    return self.destroy(self._guild)
                return

            if not isinstance(source, YTDLSource):
                # Source was probably not downloaded
                # regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'```{e}```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'Playing `{source.title}` requested by '
                                               f'{source.requester.mention}')
            await self.next.wait()

            # cleanup ffmpeg
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song
                with YoutubeDL(ytdl_options) as ydl:
                    info = ydl.extract_info(source.web_url, download=False)
                    filename = Path(ydl.prepare_filename(info)).with_suffix(".mp3")
                    try:
                        if os.path.exists(filename):
                            os.remove(filename)
                        else:
                            pass
                    except Exception as E:
                        print(E)
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """destroy the player"""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:  
            for entry in self.players[guild.id].queue._queue:
                if isinstance(entry, YTDLSource):
                    entry.__getitem__
                    entry.cleanup()
            self.players[guild.id].queue._queue.clear()
        except KeyError:
            pass                        
                       
        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('> This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('> Error connecting to Voice Channel. '
                           '> Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(aliases=['join'])
    async def connect(self, ctx, *, channel: discord.VoiceChannel=None):
        """`join` connect to voice
        This command also handles moving the bot to different channels
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('> No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'> Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'> Connecting to channel: <{channel}> timed out.')

        await ctx.send(f'Connected to: `{channel}`', delete_after=20)


    @commands.command(aliases=["stream"])
    async def play(self, ctx, *, search: str):
        """`play [url/search]` stream a song, may end abruptly because google
        join voice channel if availible
        YTDL to search and get song
        """
        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect)

        player = self.get_player(ctx)

        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @commands.command(hidden=True)
    async def download(self, ctx, *, search: str):
        """`download [url/search]` download and play song, may take a long time
        join voice channel if availible
        YTDL to search and get song
        """
        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect)

        player = self.get_player(ctx)

        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=True)

        await player.queue.put(source)
        
    @commands.command()
    async def pause(self, ctx):
        """`pause` pauses current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('> `Pause what?`', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send('> `Song paused`')

    @commands.command()
    async def resume(self, ctx):
        """`resume` resumes paused song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> `Resume what?`', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send('> `Song resumed`')

    @commands.command(aliases=['sk'])
    async def skip(self, ctx):
        """`skip` skip current song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> `Skip what?`', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send('> `Song skipped`')

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """`queue` show queue of upcoming songs"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> `Not connected to voice`', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('> `Queue empty`.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'{song["title"]}' for song in upcoming)
        # embed = discord.Embed(title='Queue', description=fmt)

        await ctx.send(f'```{fmt}```')

    @commands.command(name='playing', aliases=['np', 'current', 'currentsong'])
    async def now_playing(self, ctx):
        """`np` display information current on song"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> `Not connected to voice`', delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('> `Nothing is playing`')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'Playing `{vc.source.title}` requested by '
                                   f'{vc.source.requester.mention}')

    @commands.command(aliases=['vol', 'cv'])
    @commands.is_owner()
    async def volume(self, ctx, *, vol: float):
        """`vol <value>` change volume (owner)"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> `Not connected to voice`', delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send('> Volume can only be between `1` and `100`')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'> Volume set to `{vol}`')

    @commands.command(aliases=['leave'])
    async def stop(self, ctx):
        """`stop` destroy the player"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> `Stop what?`', delete_after=20)

        await self.cleanup(ctx.guild)


def setup(client):
    client.add_cog(Music(client))
