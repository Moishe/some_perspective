import fileinput
import nltk
import nltk.data
import words
from collections import defaultdict
from nltk.stem import SnowballStemmer
from nltk.tokenize import MWETokenizer
from nltk.tokenize import RegexpTokenizer
from nltk.util import ngrams

stemmer = SnowballStemmer("english")
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

def filterlist(wordlist):
	if type(wordlist[0]) is str:
		return [w for w in wordlist if words.is_word(w)]
	else:
		return wordlist

def get_bigrams(filename):
	text = ''
	f = open(filename, 'r')
	print "opened %s" % filename
	sentences = sent_detector.tokenize(f.read().decode('utf-8').lower())
	print "sentences: " + str(len(sentences))

	bigrams = set()
	trigrams = set()
	allwords = set()

	for sentence in sentences:
		filtered_words = nltk.word_tokenize(sentence)
		#filtered_words = [x for x in nltk.word_tokenize(sentence) if words.is_word(x)]

		for ngram in ngrams(filtered_words, 2):
			bigrams.add(str(ngram))

		for ngram in ngrams(filtered_words, 3):
			trigrams.add(str(ngram))

		for word in filtered_words:
			allwords.add(word)

	return (allwords, bigrams, trigrams)

#js = get_bigrams('controls/grapes-1.txt')
#eh = get_bigrams('controls/sunalso-1.txt')
#dg = get_bigrams('controls/flying-cars.txt')
#jds = get_bigrams('controls/rye-1.txt')

t = 0

pg = []
for i in range(1,11):
	pg.append(get_bigrams('corpora/pg' + str(i)))
	print i

sets = [x[t] for x in pg[1:]]
pgonly = pg[0][t].intersection(*sets)

print '\n'.join(pgonly)

