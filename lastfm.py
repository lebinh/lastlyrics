from urllib import quote
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup
from datetime import datetime

class LastfmError(Exception):
  def  __init__(self, error_response):
    soup = BeautifulSoup(error_response.content)
    self.error_msg = soup.find('error').string

def get_recent_tracks(username):
  "Get username's last played song from last.fm API"
  query = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=6&user=%s&api_key=4b07bbcee2b8fc6f56a338ad24cbdedf' % quote(username)
  response = urlfetch.fetch(query, headers = {'Cache-Control' : 'max-age=0'})
  if response.status_code == 200:
    soup = BeautifulSoup(response.content)
    def parse_track_tag(track):
      if track.find('date'):
        time = datetime.utcfromtimestamp(float(track.find('date')['uts']))
      else:
        time = None
      return {
        'name': track.find('name').string,
        'artist': track.find('artist').string,
        'time': time
      }
    return [parse_track_tag(track) for track in soup.findAll('track')]
  else:
    raise LastfmError(response)
    
def get_most_played_tracks(artist):
  "Get artist's most played song info from last.fm API"
  artist = quote(artist.encode('utf-8'))
  query = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&artist=%s&api_key=4b07bbcee2b8fc6f56a338ad24cbdedf' % artist
  response = urlfetch.fetch(query)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content)
    def parse_track_tag(track):
      return {
        'name': track.find('name').string,
        'playcount': track.find('playcount').string,
        'listeners': track.find('listeners').string
      }
    return [parse_track_tag(track) for track in soup.findAll('track')]
  else:
    raise LastfmError(response)

def get_similar_tracks(artist, song):
  "Get similar songs of a specified song"
  artist = quote(artist.encode('utf-8'))
  song = quote(song.encode('utf-8'))
  query = "http://ws.audioscrobbler.com/2.0/?method=track.getsimilar&artist=%s&track=%s&api_key=4b07bbcee2b8fc6f56a338ad24cbdedf" % (artist, song)
  response = urlfetch.fetch(query)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content)
    def parse_track_tag(track):
      res = {'name': track.find('name').string}
      res['artist'] = track.find('artist').find('name').string
      return res
    return [parse_track_tag(track) for track in soup.findAll('track')]
  else:
    print response.content
