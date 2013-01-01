from classifier import SentenceClassifier

class SentenceMeanClassifier(SentenceClassifier):
	"""
		Computes the mean of the scores within a sentence and (if the result's confidence
		is greater than the optional confidence parameter) returns 1 as the label if that 
		mean is greater than or equal to positive_threshold, -1 if the mean is less or 
		equal to negative_threshold and 0 otherwise. 

		The strength is the computed mean of all scores for every word.

		The confidence is the total number of unknown scores in the sentence, 
		divided by the total length of the sentence. 
	"""

	def __init__(self, positive_threshold, negative_threshold, confidence_threshold=None):

		if positive_threshold is None:
			raise ValueError("positive_threshold: can't be None")
		if negative_threshold is None:
			raise ValueError("negative_threshold: can't be None")

		if negative_threshold > positive_threshold:
			raise ValueError("negative_threshold: can't be greater than positive_threshold")

		self.positive_threshold = positive_threshold
		self.negative_threshold = negative_threshold
		self.confidence_threshold = confidence_threshold

	def classify_sentence(self, sentence):

		unknowns, words, score, scorable = 0, 0, 0, 0
		contradictions = 0

		# Work out the average score 
		for word, pos, norm, scores in sentence:
			words += 1
			if scores is None:
				unknowns += 1
				continue
			for score in scores:
				score += score['pos']
				score -= score['neg']
				scorable += 1

		# Error case for no scores
		if scorable == 0:
			return 0, 0, 0

		# Compute totals
		overall = 1.0 * score / scorable
		confidence = 1.0 - (1.0 * unknowns / words)

		# Check the confidence level
		if self.confidence_threshold is not None:
			if confidence < self.confidence_threshold:
				return 0, overall, confidence

		# Determine label
		if overall >= self.positive_threshold:
			label = 1
		elif overall <= self.negative_threshold:
			label = -1
		else:
			label = 0

		return label, overall, confidence
