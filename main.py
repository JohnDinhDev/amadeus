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


    #  def _mark_watched(self, video_id, player_response):
    #      playback_url = url_or_none(try_get(
    #          player_response,
    #          lambda x: x['playbackTracking']['videostatsPlaybackUrl']['baseUrl']))
    #      if not playback_url:
    #          return
    #      parsed_playback_url = compat_urlparse.urlparse(playback_url)
    #      qs = compat_urlparse.parse_qs(parsed_playback_url.query)
    #
    #      # cpn generation algorithm is reverse engineered from base.js.
    #      # In fact it works even with dummy cpn.
    #      CPN_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    #      cpn = ''.join((CPN_ALPHABET[random.randint(0, 256) & 63] for _ in range(0, 16)))
    #
    #      qs.update({
    #          'ver': ['2'],
    #          'cpn': [cpn],
    #      })
    #      playback_url = compat_urlparse.urlunparse(
    #          parsed_playback_url._replace(query=compat_urllib_parse_urlencode(qs, True)))
    #
    #      self._download_webpage(
    #          playback_url, video_id, 'Marking watched',
    #          'Unable to mark watched', fatal=False)


    #  def _download_webpage_handle(self, url_or_request, video_id, note=None, errnote=None, fatal=True, encoding=None, data=None, headers={}, query={}, expected_status=None):
    #      """
    #      Return a tuple (page content as string, URL handle).
    #
    #      See _download_webpage docstring for arguments specification.
    #      """
    #      # Strip hashes from the URL (#1038)
    #      if isinstance(url_or_request, (compat_str, str)):
    #          url_or_request = url_or_request.partition('#')[0]
    #
    #      urlh = self._request_webpage(url_or_request, video_id, note, errnote, fatal, data=data, headers=headers, query=query, expected_status=expected_status)
    #      if urlh is False:
    #          assert not fatal
    #          return False
    #      content = self._webpage_read_content(urlh, url_or_request, video_id, note, errnote, fatal, encoding=encoding)
    #      return (content, urlh)
    #
    #  @staticmethod
    #  def _guess_encoding_from_content(content_type, webpage_bytes):
    #      m = re.match(r'[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\s*;\s*charset=(.+)', content_type)
    #      if m:
    #          encoding = m.group(1)
    #      else:
    #          m = re.search(br'<meta[^>]+charset=[\'"]?([^\'")]+)[ /\'">]',
    #                        webpage_bytes[:1024])
    #          if m:
    #              encoding = m.group(1).decode('ascii')
    #          elif webpage_bytes.startswith(b'\xff\xfe'):
    #              encoding = 'utf-16'
    #          else:
    #              encoding = 'utf-8'
    #
    #      return encoding
    #
