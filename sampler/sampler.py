import collections
import json
import operator
import re
import robotparser
import time
import urllib2
import words

from bs4 import BeautifulSoup
from urlparse import urlparse, urlunparse

counts = collections.defaultdict(int)
seen_urls = set()
urls = []
robotfilter = None
useragent = 'Technology-Soothing-Bot/1.0'

def addbotfilter(url):
    global robotfilter
    robotfilter = robotparser.RobotFileParser(url)
    robotfilter.read()

def enqueue(url):
    global urls
    urls.append(url)

def normalize_url(seed_url, url):
    parsed_url = urlparse(url)
    parsed_seed = urlparse(seed_url)
    (scheme,netloc,path,params,query,fragment) = parsed_url
    if not scheme:
        scheme = parsed_seed.scheme
    if not netloc:
        netloc = parsed_seed.netloc

    return urlunparse((scheme, netloc, path, params, query, fragment))

def valid_url(seed_url, url):
    global seen_urls

    global robotfilter
    global useragent
    try:
        if not robotfilter.can_fetch(useragent, url):
            print 'skipping because of robots.txt: ' + url
            return False
    except:
        return False

    parsed_url = urlparse(url)
    parsed_seed = urlparse(seed_url)

    if not parsed_url.path and parsed_url.fragment:
        return False

    if parsed_seed.scheme == parsed_url.scheme and parsed_seed.netloc == parsed_url.netloc:
        return True

    if not parsed_url.scheme and not parsed_url.netloc:
        return True

    return False

def normalize_word(word):
    return word.lower()

def process_one_url():
    global urls
    global useragent

    url = urls.pop(0)
    print "LOADING: " + url

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', useragent)]
    response = opener.open(url)
    html = response.read()

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text();

    raw_words = re.compile(r'\W+', re.UNICODE).split(text)
    for word in raw_words:
        if words.is_word(word):
            counts[normalize_word(word)] += 1

    links = soup.find_all("a")
    urls += [normalize_url(url, x.attrs['href']) for x in links if 'href' in x.attrs and valid_url(url, x.attrs['href'])]

addbotfilter('http://paulgraham.com/robots.txt')
enqueue('http://paulgraham.com/vb.html')
count = 0
while count < 100 and len(urls):
    process_one_url()
    count += 1

print json.dumps(dict(sorted(counts.items(), key=operator.itemgetter(1)), indent=4, separators=(',', ': ')))
