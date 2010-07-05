import re
from urllib import quote
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError
from google.appengine.ext import db
from BeautifulSoup import BeautifulSoup, Comment

class Lyric(db.Model):
  artist = db.StringProperty(required=True)
  song = db.StringProperty(required=True)
  lyric = db.TextProperty(required=True)


class URLFetchError(Exception):
  def __init__(self, url, code):
    self.url = url
    self.code = code


def get_lyric(artist, song):
  "Search lyrics using lyrics.wikia.com API, return None if cannot find the lyric"
  query = Lyric.all().filter('artist =', artist.lower()).filter('song =', song.lower())
  result = query.fetch(1)
  if result:
    return result[0].lyric
  else:
    q_artist = quote(artist.encode('utf-8'))
    q_song = quote(song.encode('utf-8'))
    query = 'http://lyrics.wikia.com/api.php?action=lyrics&fmt=xml&func=getSong&artist=%s&song=%s' % (q_artist, q_song)
    response = urlfetch.fetch(query)
    if response.status_code == 200:
      soup = BeautifulSoup(response.content)
      lyric = soup.find('lyrics').string
      if lyric == 'Not found':
        return None
      else:
        lyric_url = soup.find('url').string
        lyric = parse_lyrics_wikia(lyric_url)
        # save the lyric to our database
        lyric_entity = Lyric(artist=artist.lower(), song=song.lower(), lyric=lyric)
        lyric_entity.put()
        return lyric
    else:
      raise URLFetchError(url, response.status_code)

def parse_lyrics_wikia(url):
  "Get lyric page from lyrics.wikia.com and parse it to get the lyric"
  page = urlfetch.fetch(url)
  soup = BeautifulSoup(page.content)
  lyric = soup.find('div', 'lyricbox')
  for div in lyric.findAll('div', 'rtMatcher'):
    div.extract()
  for comment in lyric.findAll(text=lambda text:isinstance(text, Comment)):
    comment.extract()
  lyric = unicode(lyric).replace('\n','').replace('<br />','\n')
  return ''.join(BeautifulSoup(lyric).findAll(text=True))

