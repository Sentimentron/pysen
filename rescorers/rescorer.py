#!/usr/bin/env python

import types

class Rescorer(object):

	def rescore(self, sentence):

		for word, pos, norm, scores in sentence:
			scores = self.get_score(scores)
			yield word, pos, norm, scores


	def get_score(self, score):
		pass