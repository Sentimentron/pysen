#!/usr/bin/env python

import string
from prefilter import PreFilter

class WordFilter(PreFilter):
	
	"""
		Removes any text sequence which contains non-alpha terms, strips
		punctuation from any text sequence which contains them.
	"""

	def __init__(self, punctuation=None, alphas=None):
		if punctuation is None:
			self.punctuation = set(',.!?:;()')
		else:
			self.punctuation = set(punctuation)
		if alphas is None:
			self.alphas = set(filter(lambda x: x.upper() == x, string.letters))
		else:
			self.alphas = set(alphas)

	def filter(self, sentence):
		
		buf = []

		for word in sentence:
			
			reject = False 
			filter_set = set([])
			
			for char in word:
				if char in self.punctuation:
					filter_set.add(char)
				elif char not in self.alphas:
					reject = True 
					break

			if reject:
				continue

			for char in filter_set:
				word = word.replace(char,'')

			buf.append(word)

		return ' '.join(buf)
