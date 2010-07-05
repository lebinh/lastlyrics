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
  def render_template(name, values):
    path = os.path.join(os.path.dirname(__file__), 'templates/%s.html' % name)
    self.response.out.write(template.render(path, values))
    
  def display_error(self, error_msg):
    error_msg = error_msg.replace('\n', '<br />')
    self.render_template('error', {'error_msg': error_msg})
    
  def internal_error():
    self.display_error('Something really bad happened!')


class LastfmUserHandler(BaseHandler):
  def get(self, username):
    try:
      tracks = lastfm.get_recent_tracks(username)
      template_values = {
        'username': username,
        'song': tracks[0]['name'],
        'artist': tracks[0]['artist'],
        'lyric': lyricswiki.get_lyric(tracks[0]['artist'], tracks[0]['name']),
        'related_songs': tracks[1:]
      }
      self.render_template('user', template_values)
    except lastfm.LastfmError, ex:
      error_msg = 'Error while trying to get info of user "%s" from Last.fm:\n %s' % (username, ex.error_msg)
      self.display_error(error_msg)
    except lyricswiki.URLFetchError, ex:
      error_msg = 'Error while trying to get the lyric!'
      self.display_error(error_msg)
    except Exception, ex:
      self.internal_error()


class SongHandler(BaseHandler):
  def get(self, artist, song):
    try:
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
      self.render_template('song', template_values)
    except Exception, ex:
      self.internal_error()


class ArtistHandler(BaseHandler):
  def get(self, artist):
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
      self.render_template('artist', template_values)
    except Exception, ex:
      self.internal_error()


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
