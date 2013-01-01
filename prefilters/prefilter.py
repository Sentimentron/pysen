#!/usr/bin/env python

class PreFilter(object):
	"""
		PreFilters take natural-language strings and return new strings 
		which omit some undesired feature.
	"""

	def __init__(self):
		pass

	def filter(self, sentece):
		pass

	def __call__(self, sentence):
		return self.filter(sentence)