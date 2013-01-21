import itertools
import math
import random
import sys
from types import ListType, DictType

from classifier import SentenceThresholdClassifier

def compute_cam(coverage, accuracy):
	#return 1-math.pow(accuracy, coverage)
	return math.pow(coverage, 0.55)*(accuracy-0.5)


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

	def find_threshold(self, training_sentences, desired_accuracy=1.00, desired_coverage=0.20, run_count=300):
		accuracy, coverage = 0, 1.0
		pos, neg = self.positive_threshold, self.negative_threshold
		runs = 0
		cam = compute_cam(desired_coverage, desired_accuracy)
		results = []
		while runs < run_count or len(results) == 0:

			# Generate parameters
			pos, neg = 0, 0
			while 1:
				pos = random.random()*0.5 - 0.25
				neg = 0.25-random.random()*0.5
				if pos > neg:
					break

			runs += 1
			accurate, total = 0, 0
			correct_pos, correct_neg = 0, 0
			count_pos, count_neg = 0, 0
			accuracy_pos, accuracy_neg = 0, 0
			classified = 0
			self.positive_threshold, self.negative_threshold = pos, neg
			for sentence, label in training_sentences:
				_label, _confidence, _junk = self.classify_sentence(sentence)
				total += 1
				if label == 1:
					count_pos += 1
				else:
					count_neg += 1
				if _label == 0:
					continue
				classified += 1
				if _label == label:
					accurate += 1
					if label == -1:
						correct_neg += 1
					if label == 1:
						correct_pos += 1

			accuracy_neg = 1.0 * correct_neg / count_neg 
			accuracy_pos = 1.0 * correct_pos / count_pos

			accuracy = 1.0 * accurate/classified
			coverage = 1.0 * classified/total
			new_cam  = compute_cam(coverage, accuracy)
			print >> sys.stderr, new_cam, cam
			results.append((new_cam, accuracy, coverage, pos, neg))
			print >> sys.stderr, "accuracy: %.2f %%, coverage:%.2f %%" % (accuracy*100.0, coverage*100.0)
			print >> sys.stderr, "positive: %.2f, negative:%.2f" % (pos, neg)

		winner = sorted(results, reverse=True, key=lambda x: x[0])[0]
		print >> sys.stderr, winner
		cam, accuracy, coverage, pos, neg = winner
		self.positive_threshold = pos 
		self.negative_threshold = neg
				

	def classify_sentence(self, sentence):

		unknowns, words, total_score, scorable = 0, 0, 0, 0
		contradictions = 0

		# Work out the average score 
		for word, pos, norm, scores in sentence:
			words += 1
			if scores is None:
				unknowns += 1
				continue
			if type(scores) is ListType:
				if len(scores) == 0:
					unknowns += 1
					continue
				for score in scores:
					if type(score) is DictType:
						total_score += score['pos']
						total_score -= score['neg']
					else:
						total_score += score
			else:
				if type(scores) is DictType:
					total_score += scores['pos']
					total_score -= scores['neg']
				else:
					total_score += scores 
			
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
