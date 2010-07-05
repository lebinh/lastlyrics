import os
from urllib import unquote
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import gdata.urlfetch
import gdata.service

import lastfm
import lyricswiki
import youtube

gdata.service.http_request_handler = gdata.urlfetch
webapp.template.register_template_library('template_helper')

class BaseHandler(webapp.RequestHandler):
  def display_error(self, error_msg):
    error_msg = error_msg.replace('\n', '<br />')
    path = os.path.join(os.path.dirname(__file__), 'templates/error.html')
    self.response.out.write(template.render(path, {'error_msg': error_msg}))

class LastfmUserHandler(BaseHandler):
  "Handle for user page request (/username)"

  def get(self, username):
    "Display lyric of this user most recent track"
    try:
      tracks = lastfm.get_recent_tracks(username)
      template_values = {
        'username': username,
        'song': tracks[0]['name'],
        'artist': tracks[0]['artist'],
        'lyric': lyricswiki.get_lyric(tracks[0]['artist'], tracks[0]['name']),
        'related_songs': tracks[1:]
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/user.html')
      self.response.out.write(template.render(path, template_values))
    except lastfm.LastfmError, ex:
      error_msg = 'Error while trying to get info of user "%s" from Last.fm:\n %s' % (username, ex.error_msg)
      self.display_error(error_msg)
    except lyricswiki.URLFetchError, ex:
      error_msg = 'Error while trying to fetch url: %s\nHTTP status code: %d' % (ex.url, ex.code)
      self.display_error(error_msg)
    except Exception, ex:
      error_msg = 'Something really bad happened!'
      self.display_error(error_msg)

class SongHandler(BaseHandler):
  "Handle for specified song page request (/_/artist+name/song+name)"

  def get(self, artist, song):
#    "Display lyric of this song"
#    try:
      if artist.find('%20') != -1 or song.find('%20') != -1:
        # url contains space, redirect to correct url with + instead of space
        self.redirect('/_/%s/%s' % (artist.replace('%20','+'), song.replace('%20','+')))
      artist = unicode(unquote(artist), 'utf-8').replace('+',' ')
      song = unicode(unquote(song), 'utf-8').replace('+',' ')
      similar_tracks = lastfm.get_similar_tracks(artist, song)
      template_values = {
        'song': song,
        'artist': artist,
        'lyric': lyricswiki.get_lyric(artist, song),
        'related_songs': similar_tracks[:5] if similar_tracks else None,
        'video': youtube.search('%s %s' % (song, artist))
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/song.html')
      self.response.out.write(template.render(path, template_values))
#    except Exception, ex:
#      error_msg = 'Something really bad happened!'
#      self.display_error(error_msg)

class ArtistHandler(BaseHandler):
  "Handle for artist page request (/_/artist+name)."

  def get(self, artist):
    "Display lyric of this artist most played track"
    try:
      if artist.find('%20') != -1:
        # url contains space, redirect to correct url with + instead of space
        self.redirect('/_/%s' % artist.replace('%20','+'))
      artist = unicode(unquote(artist), 'utf-8').replace('+',' ')
      tracks = lastfm.get_most_played_tracks(artist)
      template_values = {
        'song': tracks[0]['name'],
        'artist': artist,
        'lyric': lyricswiki.get_lyric(artist, tracks[0]['name']),
        'related_songs': tracks[1:6] 
      }
      path = os.path.join(os.path.dirname(__file__), 'templates/artist.html')
      self.response.out.write(template.render(path, template_values))
    except Exception, ex:
      error_msg = 'Something really bad happened!'
      self.display_error(error_msg)

class NotFoundHanlder(BaseHandler):
  def get(self):
    self.display_error("404 - Page Not Found!")

application = webapp.WSGIApplication([(r'/_/([^/]*)/([^/]*)', SongHandler),
                                      (r'/_/([^/]*)', ArtistHandler),
                                      (r'/([^/]*)', LastfmUserHandler),
                                      (r'/.*', NotFoundHanlder)],
                                      debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
