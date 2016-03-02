import argparse
import json
from keywords import keywords
import re
import urllib2
from bs4 import BeautifulSoup
from collections import defaultdict

useragent = 'Technology-Soothing-Bot/1.0'

parser = argparse.ArgumentParser(description="Score a page based on keywords")
parser.add_argument('-u', '--url', help='Page to score', required=True)
parser.add_argument('-v', '--verbose', help='Verbose', required=False, action='store_true', dest='verbose')
parser.set_defaults(verbose=False)
args = parser.parse_args()

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', useragent)]
response = opener.open(args.url)
html = response.read()

soup = BeautifulSoup(html, 'lxml')

text = ""
for eltype in ['td', 'p', 'div']:
    els = soup.find_all(eltype)
    for el in els:
        text += el.text

matches = defaultdict(int)
for k in keywords:
    if re.search(r"\b" + re.escape(k) + r"\b", text):
        matches[k] += 1

if args.verbose:
	print "%s: %s" % (args.url, json.dumps(matches))
else:
	print "%s: %s" % (args.url, str(len(matches.keys())))