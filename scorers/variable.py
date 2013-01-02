from scorer import TrainableScorer

class VariableExperienceScorer(TrainableScorer):

	"""
		The VariableExperienceScorer scores words based on the frequency
		associated with a given label observed in training data. 

		A low threshold allows ambiguous words (i.e. those with a small
		difference in the observed frequency of positive and negative 
		instances) to be scored.

	"""

	def __init__(self, feature_db, threshold = 0.0, feature_set = None):
		self.feature_db = feature_db
		self.feature_set = feature_set
		self.threshold = threshold

		if threshold < 0:
			raise ValueError("threshold: can't be less than 0")
		elif threshold > 1:
			raise ValueError("threshold: can't be greater than 1")

	def __str__(self):
		return "VariableExperienceScorer(threshold=%.2f, feature_set=%s)" % (self.threshold, self.feature_set)

	def set_threshold(self, threshold):
		self.threshold = threshold

	def get_score(self, word, extra = {}):

		pos, neg = 0, 0

		for label, extra in self.feature_db.get_feature_examples(word, self.feature_set):
			if label == 1:
				pos += 1
			elif label == -1:
				neg += 1

		total = 1.0*pos+neg 
		if total == 0:
			return None 
		diff = abs(pos-neg) * (1-self.threshold)

		# If the threshold is one:
			# For a score to be positive, it has to have a positive component
			# AND the negative score must be zero 
			# For a score to be negative, it has to have a negative component
			# AND the positive score must be zero 
		# If the threshold is a number
			# For a score to be positive, it has to have a positive component
			# greater than threshold, AND the negative score must be less than 
			# or equal to the threshold 

		if pos > diff:
			if neg <= diff:
				return [{'pos': 1, 'neg': 0}]
		if neg > diff:
			if pos <= diff:
				return [{'neg': 1, 'pos': 0}]

	def train(self, word, label, extra = {}):
		self.feature_db.add_feature_example(word, label, "pang_lee", extra)