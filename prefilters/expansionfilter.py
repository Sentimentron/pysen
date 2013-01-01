#!/usr/bin/env python

from prefilter import PreFilter

class ExpansionFilter(PreFilter):

	def filter(self, sentence):
		construct = []
		for word in sentence.split(' '):
			if "'" in word:
				if word == "it's":
					word = "it is"
				elif word == "you'd":
					word = "you would"
				elif word == "can't":
					word = "cannot"				
				elif "'ll" in word:
					word = word[0:-3] + " will"
				elif "'re" in word:
					word = word[0:-3] + " are"
				elif "n't" in word:
					word = word[0:-3] + " not"
			construct.append(word)
		return ' '.join(construct)