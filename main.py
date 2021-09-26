import os
from dotenv import load_dotenv
from cogs.MusicCog import MusicCog
load_dotenv()
from discord.ext import commands

bot = commands.Bot(command_prefix='-')
bot.add_cog(MusicCog(bot))
bot.run(os.getenv('TOKEN'))

#  from youtube_dl import YoutubeDL
#  def progress_hook(response):
#      if response['status'] == 'finished':
#          file_name = response['filename']
#          print('Downloaded ' + file_name)
#
#  options = {
#      'quiet': True,
#      'simulate': True,
#      'format': 'bestaudio',
#      'outtmpl': 'title',
#      'ignoreerrors': True,
#      'cookiefile': './cookies.txt',
#      'nocheckcertificate': True,
#      'default_search': 'auto',
#      'extract_flat': True,
#      'progress_hooks': [progress_hook]
#  }
#
#  data = YoutubeDL(options).extract_info("https://www.youtube.com/playlist?list=PLnjMQngea5YCy7qFRoTshWzksiVeoncrq")
#
#  if data is not None:
#      for jawn in data['entries']:
#          print(jawn.get('id'))
