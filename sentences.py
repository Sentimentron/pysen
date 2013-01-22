#!/usr/bin/env python

from phrases import PhraseClassifier 

class SentenceClassifier(object):

	def __init__(self, classifier=None):
		# Create a sentence classifier
		if classifier is None:
			classifier = PhraseClassifier()

		self.classifier = classifier

	def get_raw_prediction(self, classifier):
		pass 