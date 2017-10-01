import argparse
import collections
import csv
import json
import nltk
import operator
import re
import robotparser
import sys
import time
import urllib2
import words

from bs4 import BeautifulSoup
from collections import defaultdict
from urlparse import urlparse, urlunparse

counts = defaultdict(int)
seen_urls = set()
enqueued_urls = []
robotfilter = None
useragent = 'Technology-Soothing-Bot/1.0'
training_file = None
test_file = None

def addbotfilter(url):
    global robotfilter
    robotfilter = robotparser.RobotFileParser(url)
    robotfilter.read()

def enqueue(url, skip_emit=False):
    global enqueued_urls

    if url in enqueued_urls:
        return

    enqueued_urls.append([url.encode('utf-8'), skip_emit])

def clear_queue():
    global enqueued_urls
    enqueued_urls = []

def emit_sentence(sentence, is_bullshit, is_training):
    global training_file, test_file
    row = [is_bullshit, sentence.encode('utf-8').strip()]

    if is_training:
        training_file.writerow(row)
    else:
        test_file.writerow(row)

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
    global enqueued_urls
    global useragent
    global seen_urls

    (url, skip_emit) = enqueued_urls.pop(0)

    if url in seen_urls:
        return []

    print "Processing: " + url

    seen_urls.add(url)

    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', useragent)]
        response = opener.open(url)
        html = response.read()
    except:
        print "Error reading: " + url + ", skipping"
        return ""

    soup = BeautifulSoup(html, 'lxml')

    if not skip_emit:
        filtered = [s.replace('\n', ' ') for s in soup.strings if ('//' not in s) and ('{' not in s)]
        sentences = nltk.sent_tokenize(' '.join(filtered))
    else:
        sentences = []

    links = soup.find_all("a")
    for url in [normalize_url(url, x.attrs['href']) for x in links if 'href' in x.attrs and valid_url(url, x.attrs['href'])]:
        enqueue(url)

    return sentences

def crawl_source(url, count, bullshit):
    print "starting crawl at url: %s" % (url)
    parsed_start = urlparse(url)
    if not parsed_start.scheme or not parsed_start.netloc:
        print "Bad URL: " + url
        sys.exit(1)

    addbotfilter(urlunparse((parsed_start.scheme, parsed_start.netloc, 'robots.txt', '', '', '')))
    enqueue(url, True)

    sentence_counts = defaultdict(int)
    while count and len(enqueued_urls):
        sentences = process_one_url()
        for sentence in sentences:
            sentence_counts[sentence] += 1
        if len(sentences):
            count -= 1

    training = False
    for sentence in sentence_counts:
        emit_sentence(sentence, bullshit, training)
        training = not training


parser = argparse.ArgumentParser(description="Site word frequency counter")
parser.add_argument('-r', '--training_output', help='Training output file', required=True)
parser.add_argument('-e', '--test_output', help='Test output file', required=True)
parser.add_argument('-c', '--count', help='Pages to read', required=True, type=int)
args = parser.parse_args()

print args

training_file = csv.writer(open(args.training_output, 'w'))
test_file = csv.writer(open(args.test_output, 'w'))

crawl_source('https://www.mcsweeneys.net/', args.count, False)
crawl_source('https://aphyr.com/posts', args.count, False)
crawl_source('http://paulgraham.com/articles.html', args.count, False)
