#!/usr/bin/env python

class SentenceClassifier(object):
	"""
		Base class for a SentenceClassifier, which takes a list of words, part of speech tags,
		normalized words and scores and works out the overall sentiment.
	"""
	
	def __init__(self):
		pass

	def classify_sentence(self, sentence):
		"""
			Sentence is an interable object containing (word, pos, norm, scores) tuples, 
			where scores is an iterable object containing {'pos': pos_score, 'neg': neg_score}
			dictionaries. The result is a label of either -1, 0 or 1, a strength between -1 and 1,
			and a confidence level between 0 and 1. Here's what they mean:

				label:
					-1: Negative
					 0: Undetermined
					 1: Positive
				strength:
					-1: Strongly negative 
					 1: Strongly positive
				confidence:
					 0: No confidence
					 1: Absolute confidence

			Classifiers which don't support strengths or 
			confidence levels should return None in these places.
		"""
		pass