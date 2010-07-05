from urllib import quote
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup
from datetime import datetime

API_ROOT = 'http://ws.audioscrobbler.com/2.0/?api_key=4b07bbcee2b8fc6f56a338ad24cbdedf'

class LastfmError(Exception):
  def  __init__(self, error_response):
    soup = BeautifulSoup(error_response.content)
    self.error_msg = soup.find('error').string

def last_query(method, arg):
  query = API_ROOT + '&method=' + method
  for key, val in arg.items():
    query += '&%s=%s' % (key, val)
  return query

def get_recent_tracks(username):
  "Get username's last played song from last.fm API"
  query = last_query('user.getrecenttracks', {'limit': 6, 'user': quote(username)})
  response = urlfetch.fetch(query, headers = {'Cache-Control': 'max-age=0'})
  if response.status_code == 200:
    soup = BeautifulSoup(response.content)
    def parse_time(s):
        return datetime.utcfromtimestamp(float(s))
    def parse_track_tag(track):
      return {
        'name': track.find('name').string,
        'artist': track.find('artist').string,
        'time': parse_time(track.find('date')['uts']) if track.find('date') else None
      }
    return [parse_track_tag(track) for track in soup.findAll('track')]
  else:
    raise LastfmError(response)

def get_most_played_tracks(artist):
  "Get artist's most played song info from last.fm API"
  artist = quote(artist.encode('utf-8'))
  query = last_query('artist.gettoptracks',{'artist': artist})
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
  query = last_query('track.getsimilar', {'artist': artist, 'track': song})
  response = urlfetch.fetch(query)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content)
    def parse_track_tag(track):
      return {
        'name': track.find('name').string,
        'artist': track.find('artist').find('name').string
      }
    return [parse_track_tag(track) for track in soup.findAll('track')]
  else:
    raise LastfmError(response)
