from scorer import Scorer

class SWScorer(Scorer):

	"""
		A sentiwordnet scorer looks up sentiment scores for 
		individuals words within SentiWordNet 
	"""

	def __init__(self, scores):
		self.scores = scores 

	def get_score(self, word):
		if word.lower() not in self.scores:
			return None
		return self.scores[word.lower()]

	def score(self, tagged, collator):
		for scoring in tagged:
			word, pos, norm = scoring 
			score = self.get_score(word)
			self.push_to_collation(collator, scoring, score)
			yield word, pos, norm, score 