import fileinput
import itertools
import json
import nltk
import nltk.data
import words
from collections import defaultdict
from nltk.stem import SnowballStemmer
from nltk.tokenize import MWETokenizer
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams
from os import listdir
from os.path import isfile, join

stemmer = SnowballStemmer("english")
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')

def filterlist(wordlist):
	if type(wordlist[0]) is str:
		return [w for w in wordlist if words.is_word(w)]
	else:
		return wordlist

def get_bigrams(filename):
	text = ''
	f = open(filename, 'r')
	sentences = sent_detector.tokenize(f.read().decode('utf-8').lower())

	allwords = set()

	for sentence in sentences:
		#filtered_words = nltk.word_tokenize(sentence)
		#filtered_words = [x for x in nltk.word_tokenize(sentence) if words.is_word(x)]
		filtered_words = tokenizer.tokenize(sentence)
		allwords.update(filtered_words)

	return allwords


control_files = [join('controls/', f) for f in listdir('controls/') if isfile(join('controls/', f))]
control_words = set()
for f in control_files:
	control_words.update(get_bigrams(f))

#js = get_bigrams('controls/grapes-1.txt')
#eh = get_bigrams('controls/sunalso-1.txt')
#dg = get_bigrams('controls/flying-cars.txt')
#jds = get_bigrams('controls/rye-1.txt')

pg = []
c = 40
for i in range(1, c + 1):
	pg.append(get_bigrams('corpora/pg' + str(i)))

indices = range(0,10)
overlaps = defaultdict(int)
subsets = itertools.combinations(indices, 3)
for ss in subsets:
	pgs = [pg[i] for i in ss]
	ov = pgs[0].intersection(*pgs[1:])
	for o in ov:
		overlaps[o] += 1


filtered_overlaps = dict((k,v / (c + 1) + 1) for k,v in overlaps.items() if v < (c + 1) * 2)

remove_control_words = set(filtered_overlaps.keys()).difference(control_words)

print json.dumps(list(remove_control_words), sort_keys=True, indent=4, separators=(',', ': '))

