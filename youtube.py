import gdata.urlfetch
import gdata.service
import gdata.youtube
import gdata.youtube.service

def search(search_term):
  client = gdata.youtube.service.YouTubeService()
  query = gdata.youtube.service.YouTubeVideoQuery()
  query.vq = search_term.encode('utf-8')
  query.max_results = '1'
  feed = client.YouTubeQuery(query)
  return {
    'title': feed.entry[0].title.text,
    'page_url': feed.entry[0].media.player.url,
    'swf_url': feed.entry[0].GetSwfUrl(),
    'description': feed.entry[0].media.description,
    'viewcount': feed.entry[0].statistics.view_count,
    'published': feed.entry[0].published.text.split('T')[0]
  } if feed.entry else None
