class Scorer(object):
	"""
		A scorer returns a classification for units in a sequence
	"""
	def __init__(self):
		pass

	def score(self, tagged):
		"""
			Scores what, returns a number between -1 and 1, or None
			if the sentiment is unknown
		"""
		pass

	def get_score(self, word, extra={}):
		pass

class TrainableScorer(Scorer):

	def train(self, word, label, extra={}):
		pass 
