import argparse
import collections
import json
import operator
import re
import robotparser
import sys
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
    global seen_urls

    url = urls.pop(0)

    if url in seen_urls:
        return ""

    seen_urls.add(url)

    print "LOADING: " + url

    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', useragent)]
        response = opener.open(url)
        html = response.read()
    except:
        print "Error reading: " + url + ", skipping"
        return ""

    soup = BeautifulSoup(html, 'lxml')

    text = ""
    for eltype in ['td', 'p', 'div']:
        els = soup.find_all(eltype)
        for el in els:
            text += el.text

    links = soup.find_all("a")
    urls += [normalize_url(url, x.attrs['href']) for x in links if 'href' in x.attrs and valid_url(url, x.attrs['href'])]
    return text

parser = argparse.ArgumentParser(description="Site word frequency counter")
parser.add_argument('-u', '--url', help='Start crawling url', required=True)
parser.add_argument('-f', '--output', help='Output file', required=True)
parser.add_argument('-c', '--count', help='Pages to read', required=True, type=int)
args = parser.parse_args()

print args

parsed_start = urlparse(args.url)
if not parsed_start.scheme or not parsed_start.netloc:
    print "Bad URL: " + args.url
    sys.exit(0)

addbotfilter(urlunparse((parsed_start.scheme, parsed_start.netloc, 'robots.txt', '', '', '')))
enqueue(args.url)

#addbotfilter('http://www.newyorker.com/robots.txt')
#enqueue('http://www.newyorker.com/news/news-desk/the-rubio-and-cruz-delusion')
count = 0
while count < args.count and len(urls):
    text = process_one_url()
    if text:
        count += 1
    fn = args.output + str(count)
    print 'writing to %s' % (fn)
    output = open(fn, 'w')
    output.write(text.encode('utf-8'))

