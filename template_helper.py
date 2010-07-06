from google.appengine.ext import webapp

register = webapp.template.create_template_register()

def quote(s):
  return s.replace(' ','+')

def a_tag(url, text, outlink=False):
  if outlink:
    return '<a href="%s" class="outlink">%s</a>' % (url, text)
  else:
    return '<a href="%s">%s</a>' % (url, text)
    
def outlink(text, url):
  return a_tag(url, text, True)
 
def link_to_lastfm_artist(name):
  url = 'http://www.last.fm/music/%s' % quote(name)
  return a_tag(url, name, True)
  
def link_to_lastfm_user(username):
  url = 'http://www.last.fm/user/%s' % quote(username)
  return a_tag(url, username, True)

def link_to_lastfm_song(name, artist):
  url = 'http://www.last.fm/music/%s/_/%s' % (quote(artist), quote(name))
  return a_tag(url, name, True)
  
def link_to_song(name, artist):
  url = '/_/%s/%s' % (quote(artist), quote(name))
  return a_tag(url, name)

def link_to_artist(name):
  url = '/_/%s' % quote(name)
  return a_tag(url, name)

register.filter(link_to_artist)
register.filter(link_to_song)
register.filter(link_to_lastfm_user)
register.filter(link_to_lastfm_artist)
register.filter(link_to_lastfm_song)
register.filter(outlink)
