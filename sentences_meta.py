#!/usr/bin/env python

import sys

from sentences_fft import SentenceFFTClassifier
from sentences import VerySimpleSentenceClassifier, SentenceClassifier
from phrases import PhraseClassifier
from models import Sentence 

class MetaSentenceClassifier(SentenceClassifier):

	def __init__(self, engine, classifier=None):
		super(MetaSentenceClassifier, self).__init__(classifier)

		self.vss_classifier = VerySimpleSentenceClassifier(self.classifier)
		self.fft_classifier = SentenceFFTClassifier(engine, self.classifier)

	def train(self, sentence, label):
		self.fft_classifier.train(sentence, label)

	def finalize(self):
		self.fft_classifier.finalize()

	def get_prediction(self, sentence):
		self._validate_sentence(sentence)

		averages, probs = [], []
		total_pos, total_neg = 0, 0
		for cls in (self.vss_classifier, self.fft_classifier):
			try:
				label, average, prob, pos, neg = cls.get_prediction(sentence)
			except ValueError as ex:
				print >> sys.stderr, ex, cls
				continue
			if label != 0:
				return label, average, prob, pos, neg
				
			averages.append(average); probs.append(prob)
			total_pos += pos; total_neg += neg 
		
		most_probable = max(probs)
		for average, prob in zip(averages, probs):
			if prob == most_probable:
				return 0, average, prob, total_pos, total_neg

		# Should never reach here
		raise Exception((sentence, average, prob, total_pos, total_neg))
