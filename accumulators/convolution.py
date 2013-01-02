#!/usr/bin/python

from classifier import SentenceThresholdClassifier
import math

def _range(low, high, increment):
	cur = low 
	buf = []
	while cur <= high:
		buf.append(cur)
		cur += increment
	return buf

def compute_mean(of):
	total = sum(of)
	return 1.0 * total / len(of)

class SentenceConvolutionClassifier(SentenceThresholdClassifier):

	"""
		SentenceConvolutionClassifier works out the score for a 
		sentence by spreading out the scores for RB tags over a 
	"""

	def __init__(self, positive_threshold, negative_threshold, 
		spread = 4, use_sentence_length=False, 
		confidence_threshold = None,
		max_iterations = 2):
		super(SentenceConvolutionClassifier, self).__init__(positive_threshold, negative_threshold, confidence_threshold)

		self.iterations = max_iterations
		self.use_sentence_length = use_sentence_length

		# Handle spread
		if spread < 0:
			raise ValueError("spread: cannot be negative.")
		if use_sentence_length:
			if spread > 1:
				raise ValueError("spread: must be less than 1 if considering sentence length")
			if spread <= 0:
				raise ValueError("spread: must be greater than 0 if considering sentence length")
		self.spread = spread


	@classmethod
	def _compute_score(cls, scorelist):
		pos, neg = [], []
		if scorelist is None:
			return {'pos': 0, 'neg': 0}
		for score in scorelist:
			pos.append(score['pos'])
			neg.append(score['neg'])
		pos = sum(pos)*1.0/len(pos)
		neg = sum(neg)*1.0/len(neg)
		return {'pos': pos, 'neg': neg}

	def classify_sentence(self, sentence):

		# Generate an enumerated dictionary of words and scores 
		try:
			sentence_dict = dict([(i, {'word': word, 'pos': pos,'score': self._compute_score(scores)}) for i, (word, pos, norm, scores) in enumerate(sentence)])
		except TypeError as ex:
			print sentence 
			raise ex 
		sentence = sentence_dict


		# Spread the score for RB tags over adjacent ones 
		iteration, max_iterations = 0, self.iterations
		if self.use_sentence_length:
			spread = self.spread * len(sentence)
		else:
			spread = self.spread

		while iteration < max_iterations:
			iteration += 1
			for position in sentence:
				entry = sentence[position]
				affecting_pos = entry["pos"]
				if ("VB" in entry["pos"] or "NN" in entry["pos"]):
					continue
				if not ("JJ" in entry["pos"] or "RB" in entry["pos"]):
					continue
				if not "score" in entry:
					continue

				affecting_score = entry["score"]
				if affecting_score["pos"] > affecting_score["neg"]:
					affecting_score = affecting_score["pos"]
				elif affecting_score["neg"] > affecting_score["pos"]:
					affecting_score = -affecting_score["neg"]
				else:
					continue

				if "affectors" in entry:
					affecting_score *= compute_mean(entry["affectors"])

				spread_list = _range(-spread, spread+1, 1.0)
				cos_base = map(lambda x: x * math.pi / (2.0 * spread), spread_list)
				cos_list = map(lambda x: x * affecting_score, map(abs, map(math.cos, cos_base)))

				min_spread = max(0, position-spread)
				max_spread = min(len(sentence)-1, position+spread)

				spread_counter = 0
				for key in _range(min_spread, max_spread, 1.0):
					if key == position:
						continue
					entry = sentence[key]
					entry_pos = entry["pos"]
					if ("NN" in entry_pos and "JJ" in affecting_pos) or ("RB" in affecting_pos and (
							"JJ" in entry_pos or "VB" in entry_pos or "RB" in entry_pos
						)):
						if "affectors" not in entry:
							entry["affectors"] = []
						entry["affectors"].append(cos_list[spread_counter])
					if "RB" in affecting_pos and ("JJ" in entry_pos or "VB" in entry_pos or "RB" in entry_pos):
						entry["affectors"].append(cos_list[spread_counter])

					spread_counter += 1

		# Resolve the overall score via majority scoring
		pos, neg = 0, 0
		for position in sentence:
			entry = sentence[position]
			if not ("VB" in entry["pos"] or "NN" in entry["pos"] or "JJ" in entry["pos"]):
				continue
			speech = entry["pos"]
			score = entry["score"]
			if score["pos"] > score["neg"]:
				pos += 1
			if score["neg"] > score["pos"]:
				neg += 1


		if pos > neg + self.positive_threshold:
			return 1, None, None
		if neg > pos + self.negative_threshold:
			return -1, None, None
		return 0, None, None