import discord
import random
from youtube_dl import YoutubeDL
from youtube_dl.extractor import common
import asyncio
from cogs.MusicCog.Song import Song
from discord import FFmpegPCMAudio, Embed, Color
from async_timeout import timeout
 

class QueueView(discord.ui.View):
    def __init__(self, textQueue, msg, songIndex):
        super().__init__()
        self.textQueue = textQueue
        self.msg = msg
        # 0 indexed pages
        self.songIndex = songIndex

        self.pageItemCount = 20
        self.pageIndex = int(self.songIndex / self.pageItemCount)

    def setMsg(self, msg):
        self.msg = msg

    async def renderQueue(self, songIndex=None, textQueue=None, getOutput=False):
        if textQueue is not None:
            self.textQueue = textQueue
        output = "```nim\n"
        startingIndex = self.pageIndex * self.pageItemCount
        endingIndex = startingIndex + self.pageItemCount
        endingIndex = len(self.textQueue) if len(self.textQueue) < endingIndex else endingIndex

        if songIndex is not None:
            self.songIndex = songIndex
            if songIndex < startingIndex or songIndex > endingIndex:
                return

        for i in range(startingIndex, endingIndex):
            song = self.textQueue[i]
            # current track Top string
            ctTop = "    ⬐ current track \n" if i == self.songIndex else ""
            ctBottom = "\n    ⬑ current track" if i == self.songIndex else ""
            newLine = ("{ctTop}{index}. {title}{ctBottom}\n"
            .format(index=(i + 1), title=song.title, ctTop=ctTop, ctBottom=ctBottom))
            output += newLine
            if i == (len(self.textQueue) - 1):
                output += "This is the end of the queue!"

        output += "\n```"

        if getOutput is True:
            return output

        if self.msg is not None:
            await self.msg.edit(content=output)


    @discord.ui.button(label='<<', style=discord.ButtonStyle.blurple)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.pageIndex = 0
        await self.renderQueue()

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.pageIndex > 0:
            self.pageIndex = self.pageIndex - 1
        await self.renderQueue()

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        lastPageIndex = int(len(self.textQueue) / self.pageItemCount)
        remainder = len(self.textQueue) % self.pageItemCount
        if remainder == 0:
            lastPageIndex -= 1

        if self.pageIndex < lastPageIndex:
            self.pageIndex = self.pageIndex + 1
        await self.renderQueue()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='>>', style=discord.ButtonStyle.blurple)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction):
        pageIndex = len(self.textQueue) / self.pageItemCount
        remainder = len(self.textQueue) % self.pageItemCount
        if remainder == 0:
            self.pageIndex = int(pageIndex) - 1
        else:
            self.pageIndex = int(pageIndex)

        await self.renderQueue()


    @discord.ui.button(label='Go to current page', style=discord.ButtonStyle.blurple)
    async def goToCurrent(self, button: discord.ui.Button, interaction: discord.Interaction):
        pageIndex = int(self.songIndex / self.pageItemCount)
        self.pageIndex = int(pageIndex)

        await self.renderQueue()

class MusicPlayer:
    options = {
        'quiet': True,
        'simulate': True,
        'format': 'bestaudio',
        'outtmpl': 'title',
        'ignoreerrors': True,
        'cookiefile': './cookies.txt',
        'nocheckcertificate': True,
        'default_search': 'auto',
        'youtube_include_dash_manifest': False,
        'extract_flat': False,
        'mark_watched': True
    }

    radioYtdl = YoutubeDL(options)

    options['extract_flat'] = True,
    options['mark_watched'] = False
    playlistYtdl = YoutubeDL(options)

    options['extract_flat'] = False
    ytdl = YoutubeDL(options)

    del options

    def __init__(self, bot, voiceClient, textChannel, cleanup):
        self.queue = asyncio.Queue()
        self.textQueue = []
        self.voiceClient = voiceClient
        self.currentSong = None
        self.event = asyncio.Event()
        self.cleanup = cleanup
        self.textChannel = textChannel
        self.lastEmbed = None
        self.queueMsg = None
        self.textQueueIndex = 0

        self.task = bot.loop.create_task(self.audioPlayerTask())


    async def audioPlayerTask(self):

        def playNextSong(err=None):
            if err:
                print(err)
            if len(self.textQueue) > 0:
                self.textQueueIndex += 1

            self.event.set()

        while True:
            self.event.clear()
            if self.queueMsg is not None:
                await self.queueView.renderQueue(songIndex=self.textQueueIndex)

            try:
                async with timeout(300):
                    self.currentSong = await self.queue.get()
            except asyncio.TimeoutError:
                await self.destroy()

            if self.currentSong.url is None:
                self.currentSong = self.generateSong(self.currentSong.webpageUrl)

            if self.voiceClient is not None and self.currentSong.url is not None:
                self.voiceClient.play(
                        FFmpegPCMAudio(self.currentSong.url),
                        after=playNextSong)
                await self.deleteLastEmbed()
                self.lastEmbed = await self.textChannel.send(embed=self.createEmbed())

            await self.event.wait()

    def skip(self):
        self.voiceClient.stop()

    def pause(self):
        self.voiceClient.pause()

    def resume(self):
        self.voiceClient.resume()

    async def stop(self):
        del self.queue
        self.queue = asyncio.Queue()
        self.voiceClient.stop()
        del self.textQueue
        self.textQueue = []
        await self.deleteLastEmbed()
        if self.queueMsg is not None:
            await self.queueMsg.delete()
            self.queueMsg = None

    async def shuffle(self):
        alreadyPlayed = self.textQueue[0:self.textQueueIndex + 1]
        self.textQueue = self.textQueue[self.textQueueIndex + 1:]
        random.shuffle(self.textQueue)
        del self.queue
        newQueue = asyncio.Queue()
        for song in self.textQueue:
            await newQueue.put(song)
        self.queue = newQueue
        self.textQueue = alreadyPlayed + self.textQueue
        if self.queueMsg is not None:
            await self.queueView.renderQueue(textQueue=self.textQueue)

    async def handleRadioCommand(self):
        data = self.radioYtdl.extract_info(":ytrec")
        if data is not None:
            for entry in data['entries']:
                if entry is None or 'Music' not in entry['categories']:
                    continue
                id = entry['id']
                title = entry['title']
                webpageUrl = "https://www.youtube.com/watch?v={}".format(id)
                song = Song(webpageUrl, title=title)
                await self.addSong(song)

    async def handlePlaylistInput(self, link):
        data = self.playlistYtdl.extract_info(link)
        if data is not None:
            for entry in data['entries']:
                id = entry['id']
                title = entry['title']
                webpageUrl = "https://www.youtube.com/watch?v={}".format(id)
                song = Song(webpageUrl, title=title)
                await self.addSong(song)

    # Handles search inputs, ex: "keshi - drunk"
    # and a youtube link that is not a playlist
    async def handleSingleInput(self, ctx, searchInput):
        song = self.generateSong(searchInput)

        if len(self.textQueue) != 0:
            await ctx.send("Added to queue:\n```ml\n{}\n```".format(song.title))
        
        await self.addSong(song)

    def generateSong(self, searchInput):
        data = self.ytdl.extract_info(searchInput)
        title = ""
        webpageUrl = ""
        url = ""

        if data is not None:
            if data.get('entries') is not None:
                title = data['entries'][0]['title']
                webpageUrl = data['entries'][0]['webpage_url']
                url = data['entries'][0]['url']
            else:
                title = data['title']
                webpageUrl = data['webpage_url']
                url = data['url']

        return Song(webpageUrl, url=url, title=title)

    async def deleteLastEmbed(self):
        if self.lastEmbed is not None:
            await self.lastEmbed.delete()
            self.lastEmbed = None

    def createEmbed(self):
        if self.currentSong is not None:
            embed = Embed(title="Now Playing",
                    #  [text in here is displayed](redirect link when clicked on text in brackets)
                    description="[{}]({})".format(self.currentSong.title, self.currentSong.webpageUrl),
                    color=Color.dark_red())
            return embed

    async def setVoiceClient(self, voiceChannel, ctx):
        if not self.queue.empty():
            return await ctx.reply(
                    "Music player is currently being used in {}"
                    .format(self.voiceClient.channel))

        await self.voiceClient.disconnect()
        self.voiceClient = await voiceChannel.connect()

    async def addSong(self, song: Song):
        await self.queue.put(song)
        self.textQueue.append(song)


    async def printQueue(self, ctx):
        if len(self.textQueue) == 0:
            return await ctx.send("```nim\nThe queue is empty\n```")

        self.queueView = QueueView(self.textQueue, self.queueMsg, self.textQueueIndex)
        output = await self.queueView.renderQueue(getOutput=True)
        self.queueMsg = await ctx.send(output, view=self.queueView)
        self.queueView.setMsg(self.queueMsg)

    def getQueueMsg(self):
        return self.queueMsg

    async def destroy(self):
        await self.deleteLastEmbed()
        await self.voiceClient.disconnect()
        self.task.cancel()
        self.cleanup()
