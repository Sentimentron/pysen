from classifier import SentenceThresholdClassifier

class SentenceMeanClassifier(SentenceThresholdClassifier):
	"""
		Computes the mean of the scores within a sentence and (if the result's confidence
		is greater than the optional confidence parameter) returns 1 as the label if that 
		mean is greater than or equal to positive_threshold, -1 if the mean is less or 
		equal to negative_threshold and 0 otherwise. 

		The strength is the computed mean of all scores for every word.

		The confidence is the total number of unknown scores in the sentence, 
		divided by the total length of the sentence. 
	"""

	def classify_sentence(self, sentence):

		unknowns, words, total_score, scorable = 0, 0, 0, 0
		contradictions = 0

		# Work out the average score 
		for word, pos, norm, scores in sentence:
			words += 1
			if scores is None or len(scores) == 0:
				unknowns += 1
				continue
			for score in scores:
				total_score += score['pos']
				total_score -= score['neg']
				scorable += 1

		# Error case for no scores
		if scorable == 0:
			return 0, 0, 0

		# Compute totals
		overall = 1.0 * total_score / scorable
		confidence = 1.0 - (1.0 * unknowns / words)

		# Determine label
		label = self._get_label(overall, confidence)

		return label, overall, confidence
