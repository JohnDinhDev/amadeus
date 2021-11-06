from cogs.MusicCog.Song import Song
from youtube_dl import YoutubeDL
from cogs.MusicCog.MusicPlayer import MusicPlayer
from discord.ext import commands
import functools

class MusicCog(commands.Cog):

    #  data = YoutubeDL(options).extract_info("https://www.youtube.com/playlist?list=PLnjMQngea5YCy7qFRoTshWzksiVeoncrq")


    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}

    @commands.command(name="radio", aliases=['r'])
    async def radio(self, ctx):
        # if user is not in a voice channel
        if not ctx.author.voice:
            return await ctx.reply("You are not in a voice channel.")

        guildId = ctx.guild.id
        voiceChannel = ctx.author.voice.channel
        musicPlayer = self.guilds.get(guildId)
        textChannel = ctx.channel

        # if server doesn't have a running music player, make one
        if musicPlayer is None:

            # connect to user's voice channel
            voiceClient = await voiceChannel.connect()

            # create cleanup function (ran when bot disconnects)
            cleanup = functools.partial(self.cleanup, guildId)

            # create MusicPlayer
            musicPlayer = MusicPlayer(self.bot, voiceClient, textChannel, cleanup)

            self.guilds[guildId] = musicPlayer

        # if music player is already in another channel, connect to it
        if (voiceChannel.id != musicPlayer.voiceClient.channel.id):
            # setVoiceClient does not connect if music player queue is not empty
            await musicPlayer.setVoiceClient(voiceChannel, ctx)


        await musicPlayer.handleRadioCommand()


    @commands.command(name="play", aliases=['p'])
    async def play(self, ctx, *, searchInput):
        # if user is not in a voice channel
        if not ctx.author.voice:
            return await ctx.reply("You are not in a voice channel.")

        guildId = ctx.guild.id
        voiceChannel = ctx.author.voice.channel
        musicPlayer = self.guilds.get(guildId)
        textChannel = ctx.channel

        # if server doesn't have a running music player, make one
        if musicPlayer is None:

            # connect to user's voice channel
            voiceClient = await voiceChannel.connect()

            # create cleanup function (ran when bot disconnects)
            cleanup = functools.partial(self.cleanup, guildId)

            # create MusicPlayer
            musicPlayer = MusicPlayer(self.bot, voiceClient, textChannel, cleanup)

            self.guilds[guildId] = musicPlayer

        # if music player is already in another channel, connect to it
        if (voiceChannel.id != musicPlayer.voiceClient.channel.id):
            # setVoiceClient does not connect if music player queue is not empty
            await musicPlayer.setVoiceClient(voiceChannel, ctx)

        isLink = searchInput.startswith("https://")
        isPlaylist = isLink and "&list=" in searchInput or isLink and "?list=" in searchInput

        if isPlaylist:
            await musicPlayer.handlePlaylistInput(searchInput)
        else:
            await musicPlayer.handleSingleInput(ctx, searchInput)

    @commands.command()
    async def stop(self, ctx):
        guildId = ctx.guild.id
        musicPlayer = self.guilds.get(guildId)

        if musicPlayer is not None:
            await musicPlayer.stop()


    @commands.command()
    async def resume(self, ctx):
        guildId = ctx.guild.id
        musicPlayer = self.guilds.get(guildId)

        if musicPlayer is not None and musicPlayer.voiceClient.is_playing:
            musicPlayer.resume()

    @commands.command()
    async def pause(self, ctx):
        guildId = ctx.guild.id
        musicPlayer = self.guilds.get(guildId)

        if musicPlayer is not None and musicPlayer.voiceClient.is_playing:
            musicPlayer.pause()

    @commands.command()
    async def skip(self, ctx):
        guildId = ctx.guild.id
        musicPlayer = self.guilds.get(guildId)

        if musicPlayer is not None and musicPlayer.voiceClient.is_playing:
            musicPlayer.skip()
            if musicPlayer.queue.empty():
                await musicPlayer.deleteLastEmbed()

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        guildId = ctx.guild.id
        musicPlayer = self.guilds.get(guildId)
        if musicPlayer is not None:
            return await musicPlayer.printQueue(ctx)
        else:
            return await ctx.send("```nim\nThe queue is empty\n```")

    @commands.command()
    async def shuffle(self, ctx):
        guildId = ctx.guild.id
        musicPlayer = self.guilds.get(guildId)

        if musicPlayer is not None:
            await musicPlayer.shuffle()

    def cleanup(self, guildId):
        del self.guilds[guildId]

