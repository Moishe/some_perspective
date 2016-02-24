from bs4 import BeautifulSoup
import collections
import operator
import urllib2

counts = collections.defaultdict(int)
urls = []

def enqueue(url):
    global urls
    urls.append(url)

def normalize_url(seed_url, url):
    print url

def local_url(url):
    return True

def process_one_url():
    global urls
    url = urls.pop(0)
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text();

    words = text.split()
    for word in words:
        counts[word] += 1

    links = soup.find_all("a")
    urls += [normalize_url(url, x.attrs['href']) for x in links if 'href' in x.attrs and local_url(x.attrs['href'])]



enqueue('http://paulgraham.com/vb.html')
process_one_url()

print sorted(counts.items(), key=operator.itemgetter(1))
