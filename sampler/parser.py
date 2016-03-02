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
from random import shuffle

stemmer = SnowballStemmer("english")
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')

def get_bigrams(filename):
	text = ''
	f = open(filename, 'r')
	print "reading %s" % filename
	sentences = sent_detector.tokenize(f.read().decode('utf-8').lower())

	allwords = set()

	for sentence in sentences:
		#filtered_words = nltk.word_tokenize(sentence)
		#filtered_words = [x for x in nltk.word_tokenize(sentence) if words.is_word(x)]
		filtered_words = [x for x in tokenizer.tokenize(sentence) if words.is_word(x)]
		allwords.update(filtered_words)

	return allwords

def words_from_directory(directory, max_files):
	files = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]
	if max_files < len(files):
		print "every day I'm shufflin' shufflin' %s" % str(files)
		shuffle(files)
		files = files[:max_files]

	wordsets = []
	for f in files:
		wordsets.append(get_bigrams(f))

	return wordsets

control_file_count = 10
corpus_file_count = 10
c = 3

control_word_sets = words_from_directory('controls/', control_file_count)
corpus_word_sets = words_from_directory('corpora/', corpus_file_count)

indices = range(0, len(corpus_word_sets))
overlaps = defaultdict(int)
subsets = itertools.combinations(indices, c)
for ss in subsets:
	pgs = [corpus_word_sets[i] for i in ss]
	ov = pgs[0].intersection(*pgs[1:])
	for o in ov:
		overlaps[o] += 1


filtered_overlaps = dict((k,v / (c + 1) + 1) for k,v in overlaps.items() if v < (c + 1) * 2)

remove_control_words = set(filtered_overlaps.keys()).difference(*control_word_sets)

print json.dumps(list(remove_control_words), sort_keys=True, indent=4, separators=(',', ': '))

