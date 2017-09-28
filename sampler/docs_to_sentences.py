import nltk
import os

#
# Make sure we have the sentence-splitting data for nltk
#

nltk.download('punkt')

# for every document

counter = 0
directory = 'corpora'

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')


for filename in os.listdir(directory):
	content = open('corpora/' + filename, 'r').read().decode('utf-8')
	sentences = sent_detector.tokenize(content)

	print sentences[2]