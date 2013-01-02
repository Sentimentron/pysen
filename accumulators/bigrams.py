from classifier import SentenceThresholdClassifier

class SentenceBigramClassifier(SentenceThresholdClassifier):

	"""
		This classifer splits a sentence into bigrams, in order to better handle different
		POS tags. It filters the bigrams to ensure that they're likely to convey sentiment,
		then works out the average score of all of the scorable bigrams, assigns 1 as the 
		label if this is equal to or over the positive_threshold, assigns -1 if this is 
		less than the negative_threshold and assigns 0 otherwise. 

		The strength is the average score for all bigrams. 

		The confidence is the number of bigrams containing at least one unknown, divided by 
		the total number of bigrams.

	"""

	@classmethod
	def _generate_bigrams(cls, of_what):
		return zip(of_what[0:-1], of_what[1:])

	@classmethod
	def _map_pos(cls, tag):
		if "JJ" in tag or "RB" in tag or "VB" in tag or "NN" in tag:
			return tag 

	@classmethod
	def _check_bigram_meaningful(cls, clause1, clause2):
		if clause1[1] is None or clause[2] is None:
			return False
		return True

	@classmethod 
	def _compute_score(cls, scorelist):
		pos, neg = [], []
		for score in scorelist:
			pos.append(score['pos'])
			neg.append(score['neg'])
		means = map(compute_mean, [pos, neg])
		variances = map(compute_variance, [pos, neg])
		variances = map(math.sqrt, variances)
		scores = map(lambda x: x[0] + x[1], zip(means, variances))

		return {'pos': scores[0], 'neg': scores[1]}

	@classmethod
	def _generate_bigramscore(cls, bigram):
		"""
			Computes the pos/neg score for a bigram and returns it 
			alongside the number of unknown scores.
		"""
		part1, part2 = bigram
		accum, subtotal = {'pos': 0, 'neg': 0}, {'pos': 1, 'neg': 1}
		pos1, pos2 = part1[1], part2[1]
		modify = False 
		unknowns = 0

		# Work out modification status
		if "RB" in pos1 or "RB" in pos2:
			if "RB" in pos1 and "RB" in pos2:
				pass 
			else:
				modify = True 
		if "JJ" in pos1 or "JJ" in pos2:
			if "JJ" in pos1 and "JJ" in pos2:
				pass
			else:
				modify = True 
		
		for part in bigram:
			word, pos, norm, scores = part
			if scores is None:
				unknowns += 1
				continue
			score = self._compute_score(scores)
			if ("RB" in pos or "JJ" in pos) and modify:
				for key in accum:
					accum[key] += score[key]
		
		for key in accum:
			subtotal[key] *= 1.0 + accum[key]

		return subtotal['pos'], subtotal['neg'], unknowns

	def classify_sentence(self, sentence):
		
		# Compute sentence bigrams
		bigrams = self._generate_bigrams(sentence)

		# Filter sentence bigrams
		bigrams = filter(lambda x: self._check_bigram_meaningful(*x), bigrams)

		# Generate bigram scores
		scores = map(lambda x: self._generate_bigramscore, bigrams)

		# Work out the average scores
		pos_total, neg_total, unknowns, count = 0, 0, 0, 0
		for pos, neg, unknown in scores:
			count += 1
			pos_total += pos 
			neg_total += neg 
			unknowns += unknown

		pos = 1.0 * pos_total / count 
		neg = 1.0 * neg_total / count 
		unknowns = 1.0 * unknowns / count 

		overall = pos - neg
		
		# Check the confidence boundary
		if self.confidence_threshold is not None:
			if unknowns < self.confidence_threshold:
				return 0, overall, unknowns

		# Determine label
		label = self._get_label(overall, unknown)

		# Return the result
		return label, overall, unknowns