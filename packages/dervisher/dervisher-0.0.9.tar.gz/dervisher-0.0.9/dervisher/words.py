__author__ = 'lsamaha'

import random

class Words(object):

    path = None
    nouns = []
    verbs = []
    adjectives = []
    adverbs = []

    def __init__(self, path='samples'):
        self.path = path
        self.nouns = self.load_words('nouns')
        self.verbs = self.load_words('verbs')
        self.adjectives = self.load_words('adjectives')
        self.adverbs = self.load_words('adverbs')

    def any_noun(self):
        return self.any(self.nouns)

    def any_verb(self):
        return self.any(self.verbs)

    def any_adjective(self):
        return self.any(self.adjectives)

    def any_adverb(self):
        return self.any(self.adverbs)

    def any(self, words):
        return random.choice(words).strip()

    def load_words(self, type):
        try:
            fname = "%s/%s" % (self.path, type)
            with open(fname) as f:
                words = f.readlines()
        except:
            words = ['fee','fie','foe','fum']
        return words
