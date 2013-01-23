#!/usr/bin/env python

import sys

from phrases import PhraseClassifier 
from models  import Sentence 

class SentenceClassifier(object):

	def __init__(self, classifier=None):
		# Create a sentence classifier
		if classifier is None:
			classifier = PhraseClassifier()

		self.classifier = classifier

	@classmethod
	def _validate_sentence(cls, sentence):
		if not isinstance(sentence, Sentence):
			raise TypeError((sentence, "Should be a Sentence."))

	def get_raw_prediction_data(self, sentence):
		self._validate_sentence(sentence)
		scores, probs = [], []
		for phrase in sentence.phrases:
			label, score, estimate = self.classifier.get_prediction(phrase)
			scores.append(score)
			probs.append(estimate)

		comps = sentence.structure_bag_pos

		if len(scores) == 0:
			return None

		return scores, probs, comps

	def get_csv_prediction_data(self, sentence):

		raw = self.get_raw_prediction_data(sentence)
		if raw is None:
			return None 
		scores, probs, comps = raw

		average_score = sum(scores) / len(scores)
		average_probs = sum(probs ) / len(probs )

		ret = [comps['CC'], comps[','], len(scores), average_score, average_probs]

		for index in range(4):
			if index >= len(scores):
				ret.append(0.0)
			else:
				ret.append(scores[index])

		for index in range(4):
			if index >= len(probs):
				ret.append(0.0)
			else:
				ret.append(probs[index])

		return ret

	def evaluate(self, training_data):
		results = {}
		probs   = {}

		for sentence, _label in training_data:
			label, score, estimate = self.get_prediction(sentence)
			print label, score, estimate
			result_key = (_label, label)
			if result_key not in results:
				results[result_key] = []
			results[result_key].append(estimate)
		
		for key in results:
			estimates = results[key]
			count = len(estimates)
			total = sum(estimates)
			if count == 0:
				average = 0
			else:
				average = 1.0*total/count 
			probs[key] = average 

		return results, probs

class MajoritySentenceClassifier(SentenceClassifier): # 64.64% (CC), 61.8% (,), 63.42 (CC+,)
	def get_prediction(self, sentence):
		self._validate_sentence(sentence)
		pos_counts = sentence.structure_bag_pos
		for pos, count in pos_counts.most_common(2):
			print pos
			if pos not in [",", "CC"]:
				raise ValueError((sentence, "Wrong structure."))

		raw = self.get_raw_prediction_data(sentence)
		if raw is None:
			return 0, 0, 0
		scores, probs, comps = raw

		pos, neg, label = 0, 0, 0
		for score in scores:
			if score > 0.19733:
				pos += 1
			if score < 0.01468:
				neg += 1

		if pos > neg:
			label = 1
		if neg > pos:
			label = -1

		average_probs = sum(probs ) / len(probs )
		average_score = sum(scores) / len(scores)
		if average_probs <= 0.5:
			label = 0

		return label, average_score, average_probs

class FlippingSentenceClassifier(SentenceClassifier): # %55

	def get_prediction(self, sentence):
		self._validate_sentence(sentence)
		pos_counts = sentence.structure_bag_pos
		for pos, count in pos_counts.most_common(1):
			if pos not in ["."]:
				raise ValueError((sentence, "Wrong structure."))

		raw = self.get_raw_prediction_data(sentence)
		if raw is None:
			return 0, 0, 0
		scores, probs, comps = raw

		label = 0
		for score in scores:
			if score > 0.19733:
				if label != -1:
					label = 1
			if score < 0.01468:
				if label == -1:
					label = 1
				else:
					label = -1

		average_probs = sum(probs ) / len(probs )
		average_score = sum(scores) / len(scores)
		if average_probs <= 0.5:
			label = 0

		return label, average_score, average_probs

class VerySimpleSentenceClassifier(SentenceClassifier): # 73.45%

	def get_prediction(self, sentence):
		self._validate_sentence(sentence)
		pos_counts = sentence.structure_bag_pos
		for pos, count in pos_counts.most_common(1):
			if pos not in ["."]:
				raise ValueError((sentence, "Wrong structure."))

		raw = self.get_raw_prediction_data(sentence)
		if raw is None:
			return 0, 0, 0
		scores, probs, comps = raw

		#average_score = sum(scores) / len(scores)
		average_score = 0
		average_probs = sum(probs ) / len(probs )
		if average_probs > 0:
			average_score = 0
			for score, prob in zip(scores, probs):
				average_score += score*prob 
			average_score /= average_probs
			average_score /= len(scores)

		label = None 
		if average_score > 0.19733:
			label = 1
		elif average_score < 0.01468:
			label =-1
		else:
			label = 0

		if average_probs <= 0.5:
			label = 0

		return label, average_score, average_probs