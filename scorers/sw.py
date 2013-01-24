from scorer import Scorer

class SWScorer(Scorer):

	"""
		A sentiwordnet scorer looks up sentiment scores for 
		individuals words within SentiWordNet 
	"""

	def __init__(self, scores):
		self.scores = scores 

	def get_score(self, word, extra={}):
		if word.lower() not in self.scores:
			return None
		return self.scores[word.lower()]

	def score(self, tagged):
		for scoring in tagged:
			word, pos, norm = scoring 
			score = self.get_score(word)
			yield word, pos, norm, score 

class SWPOSScorer(SWScorer):

	def __init__(self, scores):
		super(SWPOSScorer, self).__init__(scores)

	def get_score(self, word, pos):
		ret = []
		
		if word.lower() not in self.scores:
			return None

		if "VB" in pos:
			pos = "v"
		elif "NN" in pos:
			pos = "n"
		elif "JJ" in pos:
			pos = "a"
		elif "RB" in pos:
			pos = "r"
		else:
			return super(SWPOSScorer, self).get_score(word)
		
		ret = filter(lambda x: x['partofspeech'] == pos, self.scores[word.lower()])
		if len(ret) > 0:
			return ret 

		return super(SWPOSScorer, self).get_score(word)

	def score(self, tagged):
		for scoring in tagged:
			word, pos, norm = scoring
			score = self.get_score(word, pos)
			yield word, pos, norm, score
