import json
from keywords import keywords
import re
from collections import defaultdict
from os import listdir
from os.path import isfile, join


def count_words_by_file(directory):
    files = [join(directory, f) for f in listdir(directory) if isfile(join(directory, f))]

    wordsets = []
    for filename in files:
        f = open(filename, 'r')
        text = f.read()

        matches = defaultdict(int)
        for k in keywords:
            if re.search(r"\b" + re.escape(k) + r"\b", text):
                matches[k] += 1

        print "%s: %s" % (filename, str(len(matches.keys())))

count_words_by_file('corpora')