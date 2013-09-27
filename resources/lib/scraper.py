import urllib2
import re
from urllib import quote
from BeautifulSoup import BeautifulSoup

MAIN_URL = 'http://www.ulmen.tv'
USER_AGENT = 'XBMC Add-on ulmen.tv'

class NetworkError(Exception):
    pass

def get_categories():
    url = MAIN_URL
    categories = []
    ul = __get_tree(url).find('ul',{'class':'level_2 children_12'})
    for li in ul.findAll('li'):
        categories.append({
            'path': li.findAll('a')[0]['href'],
            'title': li.findAll('a')[0].string.replace('&#x27;',"'")
        })
    return categories

def get_videos(path,season):
    if path[0:1] == "/":
        path = MAIN_URL+path

    page = __get_tree(path,False)
    regex_js = re.compile('window\.channel\.set\(\{(.*?)\}\)',re.DOTALL)
    regex_js_seasons = re.compile('\[(?P<sessionId>[0-9]*), "(?P<sessionName>.*?)", \[(?P<sessionContent>\[.*?\])\]\]',re.DOTALL)
    regex_js_seasons_episodes = re.compile('\[(?P<id>[0-9]*), "(?P<name>.*?)", "(?P<img>.*?)", ".*?", "(?P<path>.*?)", "(?P<length>.*?)", "(?P<date>.*?)", [0-9]*\]')
    js = regex_js.search(page).group(1)
    
    items = []
    seasons = tuple(regex_js_seasons.finditer(js));
    
    if len(seasons) == 0:
        return items
    
    for season_iter in seasons:
        seasonId = season_iter.group('sessionId')
        seasonName = season_iter.group('sessionName')
        seasonContent = season_iter.group('sessionContent')
        
        if len(seasons) > 1 and season == '0':
            items.append({
                'type':'season',
                'id':seasonId,
                'title':seasonName
            })
        elif season=='0' or season==seasonId:
            for js_seasons_episodes in regex_js_seasons_episodes.finditer(seasonContent):
                items.append({
                    'type': 'video',
                    'title': js_seasons_episodes.group('name'),
                    'id': js_seasons_episodes.group('path'),
                    'path': js_seasons_episodes.group('path'),
                    'length': js_seasons_episodes.group('length'),
                    'date': js_seasons_episodes.group('date'),
                    'img': MAIN_URL+js_seasons_episodes.group('img')
                })
    return items

    
def get_video_urls(videoId):
    url = MAIN_URL+videoId
    souptree = __get_tree(url)
    video_name = souptree.find('meta',{'property':'og:title'})['content']
    print video_name
    
    #uwe-hat-kein-bock-1-1_rainer-bruderle-1-1_rainer-bruderle-1.mp4
    
    #rtmp://178.23.127.5:1935/vod/mp4:2_SB_2_1.mp4
    
    video_urls = {
                  'SD':channel.findAll('media:content')[0]['url'],
                  'HD':channel.findAll('media:content')[1]['url']
    }
    return video_urls
    
def get_search_path(search_string):
    return '/suche/index.html?suchbegriff=%s&suchart=videos' % quote(search_string)

  
def __get_tree(url,soup=True):
    log('__get_tree opening url: %s' % url)
    headers = {}
    req = urllib2.Request(url, None, headers)
    try:
        html = urllib2.urlopen(req).read()
    except urllib2.HTTPError, error:
        raise NetworkError('HTTPError: %s' % error)
    log('__get_tree got %d bytes' % len(html))
    if soup:
        tree = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        return tree
    else:
        return html

def log(msg):
    print(u'%s scraper: %s' % (USER_AGENT, msg))