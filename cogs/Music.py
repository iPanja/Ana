import discord
from discord.ext import commands
import pafy, urllib, re
from typing import List, Union

def setup(bot):
    try:
        bot.add_cog(Music(bot))
        print("[Music* Module Loaded]")
    except Exception as e:
        print(" >> Music* Module: {0}".format(e))
    

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.bot.config
        # Settings
        self.volume = self.config['Music']['volume']
        self.voice_client = None
        # Queue
        self.music_queue: List[int] = []
        self.is_playing = False
    
    @commands.command(aliases=['connect'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def join(self, ctx: commands.Context):
        # If the bot is already in a voice channel
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            return
        
        if ctx.author.voice != None:
            # Get voice channel that the command-issuer is in
            author: discord.Member = ctx.author
            vc: discord.VoiceChannel = author.voice.channel
            # Join the channel
            self.voice_client = await vc.connect()
            await ctx.send('Joined {}'.format(vc))
            await ctx.message.delete()

            # Play song
            #source = await discord.FFmpegOpusAudio.from_probe("/Users/fhenneman/Documents/GitHub/Ana/BR2049_Mesa.mp3")
            #self.voice_client.play(source)

        else:
            await ctx.send('You must be in a voice channel to use this command!')
    
    @commands.command(aliases=['disconnect', 'stop'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def leave(self, ctx: commands.Context):
        if self.voice_client != None:
            await self.voice_client.disconnect()
            await ctx.send('Left {}'.format(self.voice_client.channel))
            self.voice_client = None
            await ctx.message.delete()
        
    @commands.command()
    async def play(self, ctx: commands.Context):
        #https://stackoverflow.com/questions/66115216/discord-py-play-audio-from-url
        msg = ctx.message.content
        if 'youtube.com/watch?v=' in msg:
            video_id = re.findall(r"watch\?v=(\S{11})", msg)[0]
        else:
            search = msg.replace(' ', '+')
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            video_id = video_ids[0]
        # Play/Queue Song
        if not self.is_playing:
            await ctx.send(f"Now playing: https://www.youtube.com/watch?v={video_id}")
        else:
            await ctx.send(f"Adding song to queue (Position {len(self.music_queue)+1})")
        self.queue(video_id)
    
    @commands.command()
    async def play_local(self, ctx: commands.Context, filename: str):
        self.queue(filename)
        
    
    @commands.command()
    async def skip(self, ctx: commands.Context):
        self.voice_client.stop()
        self.on_song_completion(error=None)
    
    @commands.command()
    async def pause(self, ctx: commands.Context):
        self.voice_client.pause()
    
    @commands.command()
    async def resume(self, ctx: commands.Context):
        self.voice_client.resume()
    
    @commands.command()
    async def clear(self, ctx: commands.Context):
        self.music_queue.clear()
        await ctx.send(f"Queue cleared")
    
    @commands.command()
    async def volume(self, ctx: commands.Context, volume: float):
        self.volume = volume
        await ctx.send(f"Volume set to {self.volume}")

    
    @play.before_invoke
    async def ensure_vc(self, ctx):
        #https://stackoverflow.com/questions/66115216/discord-py-play-audio-from-url
        if ctx.voice_client is None:
            #await self.join(ctx)
            if ctx.author.voice:
                self.voice_client = await ctx.author.voice.channel.connect()
            else:
                await ctx.send('You must be in a voice channel to use this command!')
                raise commands.CommandError("Author not connected to a voice channel.")



    # /// Helpers
    # Get a playable audio source from a YouTube video url
    def get_source_from_yt_url(self, url: str):
        video = pafy.new(url)
        best_quality_audio = video.getbestaudio()
        # FFMPEG
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(best_quality_audio.url, **self.config['Music']['ffmpeg_settings']), self.volume)
        return source
    def get_source_from_local(self, filename: str):
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=f"files/{filename}"), self.volume)
        return source
    
    # Add YT video_id to end of queue, if queue is empty immediately play the song
    def queue(self, video_id: Union[int, str]):
        if len(self.music_queue) == 0 and not self.is_playing:
            self.play_song(video_id)
        else:
            self.music_queue.append(video_id)      

    # Physically play given song via its YouTube video id
    def play_song(self, video_id: str):
        self.is_playing = True
        if video_id[0] == '.': # Local files
            source = self.get_source_from_local(filename=video_id[1::])
        else: # Youtube video id
            source = self.get_source_from_yt_url("https://www.youtube.com/watch?v=" + video_id)
        self.voice_client.play(source, after=self.on_song_completion) # On song completion, queue up the next song
    
    # /// Events
    # On song completion, queue up the next song
    def on_song_completion(self, error):
        if len(self.music_queue) > 0:
            self.play_song(self.music_queue.pop(0))
        else:
            self.is_playing = False