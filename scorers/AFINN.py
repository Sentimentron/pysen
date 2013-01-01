#!/usr/bin/env python

from scorer import Scorer
from sw import SWScorer

def read_AFINN_file(fp):

	ret = {}
	for line in fp:

		fields = line.split('\t')
		fields = map(lambda x: x.strip(), fields)

		if len(filter(lambda x: len(x) == 0, fields)) > 0:
			continue

		word = fields[0]
		score = float(fields[1])
		score_dict = {'pos': 0, 'neg': 0}
		if score < 0:
			score_dict['neg'] = abs(score)/5.0
		elif score > 0:
			score_dict['pos'] = score/5.0

		ret[word] = score 

	return ret

class AFINNScorer(Scorer):

	def __init__(self, filename):

		fp = open(filename, 'r')
		self.filename = filename 
		self.scorer = SWScorer(read_AFINN_file(fp))

	def get_score(self, word, extra= {}):
		return self.scorer.get_score(word, extra)

	def score(self, tagged):
		return self.scorer.score(tagged)