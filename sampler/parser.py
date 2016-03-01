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

	sentences = sent_detector.tokenize(f.read().decode('utf-8').lower())

	bigrams = set()
	trigrams = set()
	allwords = set()

	for sentence in sentences:
		filtered_words = [w for w in nltk.word_tokenize(sentence) if words.is_word(w)]

		for ngram in ngrams(filtered_words, 2):
			bigrams.add(str(ngram))

		for ngram in ngrams(filtered_words, 3):
			trigrams.add(str(ngram))

		for word in filtered_words:
			allwords.add(word)

	return (allwords, bigrams, trigrams)

pg = get_bigrams('pg-1.txt')
js = get_bigrams('grapes-1.txt')
eh = get_bigrams('sunalso-1.txt')
dg = get_bigrams('flying-cars.txt')
jds = get_bigrams('rye-1.txt')

t = 0

pg_prime = pg[t].difference(js[t], eh[t], dg[t], jds[t])

pg2 = get_bigrams('pg-2.txt')
print '\n'.join(pg2[t].intersection(pg_prime))

