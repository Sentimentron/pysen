#!/usr/bin/env python

from collections import Counter

from phrase import Phrase

class Sentence(object):

	def __init__(self, nlp_sentence, tagger): 

		# Can't deal with brackets
		if "[" in nlp_sentence or "(" in nlp_sentence:
			raise ValueError("Can't parse")

		self.text = nlp_sentence

		tagged = tagger.tag(nlp_sentence)
		p = Phrase()
		accum = []
		for word, pos, norm in tagged:
			try:
				p.add_word(word, pos)
			except ValueError:
				if len(p) > 0:
					accum.append(p)
				p = Phrase()
				accum.append((word, pos))
		if len(p) > 0:
			accum.append(p)
		self.vector = accum

	def __str__(self):
		return self.text.encode('ascii', 'ignore')

	def __repr__(self):
		return "Sentence(%s)" % (self.text)

	@property
	def phrases(self):
		return filter(lambda x: isinstance(x, Phrase), self.vector)

	@property 
	def remainder(self):
		return filter(lambda x: not isinstance(x, Phrase), self.vector)

	@property 
	def structure_bag(self):
		return Counter(self.remainder)

	@property 
	def structure_bag_pos(self):
		return Counter([pos for word, pos in self.remainder])