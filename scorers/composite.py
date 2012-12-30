from scorer import TrainableScorer

class BasicCompositeScorer(TrainableScorer):

	def __init__(self):
		self.scorers = []

	def _get_trainable(self):
		for scorer in self.scorers:
			if isinstance(scorer, TrainableScorer):
				yield scorer

	def get_score(self, word, extra = {}):
		for scorer in self.scorers:
			try:
				score = scorer.get_score(word, extra)
			except TypeError as ex:
				raise TypeError(str(type(scorer)) + ": " + str(ex))
			if score is not None:
				return score 
		return None 

	def train(self, word, label, extra = {}):
		for scorer in self._get_trainable():
			scorer.train(word, label, extra)

	def push(self, scorer):
		if not isinstance(scorer, Scorer):
			raise TypeError("scorer: must be a Scorer")
		self.scorers.append(scorer)