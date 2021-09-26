from discord.ext import commands
class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}

    @commands.command()
    async def play(self, ctx, *, searchInput):
        is_link = searchInput.startswith('https://')
        await ctx.send(searchInput)
