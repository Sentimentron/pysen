#!/usr/bin/env python

from readers import basic
from taggers import TopiaTagger
from models import Phrase
from accumulators import SentenceMeanClassifier
from rescorers import MaximumRescorer
from scorers import AFINNScorer, SWPOSScorer, AllScoresCompositeScorer
from estimators import WordExperienceEstimator
from readers.sw_reader import read_sen_file

class PhraseClassifier(object):

	def __init__(self, scorer = None, rescorer = None, classifier = None):

		if scorer is None:
			afinn_111 = AFINNScorer("AFINN-111.txt")
			afinn_96 = AFINNScorer("AFINN-96.txt")
			scores = read_sen_file(open('SentiWordNet_3.0.0_20120510.txt','r'))
			wexp = WordExperienceEstimator("sqlite:///words.db")
			pos_scorer = SWPOSScorer(scores)
			scorer = AllScoresCompositeScorer()
			for s in (afinn_111, afinn_96, pos_scorer):
				scorer.push(s)

		if rescorer is None:
			rescorer = MaximumRescorer()

		if classifier is None:
			classifier = SentenceMeanClassifier(0.19733, 0.01468)

		self.scorer = scorer 
		self.rescorer = rescorer
		self.classifier = classifier
		self.wexp = wexp

	@classmethod
	def __validate_phrase(cls, phrase):
		if not isinstance(phrase, Phrase):
			raise TypeError((phrase, "Needs to be a pysen.models.Phrase"))

	def get_prediction(self, phrase):
		self.__validate_phrase(phrase)

		scored = list(self.rescorer.rescore(self.scorer.score(phrase.yield_scorable())))
		estimates, estimate = [], 0
		for word, pos, norm, score in scored:
			if score == None:
				estimates.append(0.5)
				continue
			estimate = self.wexp.get_estimate_fromscore(word, score)
			estimates.append(estimate)
		if len(estimates) == 0:
			estimate = 0
		else:
			estimate = sum(estimates)/len(estimates)

		label, score, _junk = self.classifier.classify_sentence(scored)

		if False:
			if label == -1:
				if estimate <= 0.4444:
					label = 1
				else:
					label = -1
			elif label == 1:
				if estimate <= 0.375:
					label = -1
				else:
					label = 1

		return label, score, estimate 

	def train_classifier(self, training_data):
		training = []
		for phrase, label in training_data:
			scored = list(self.rescorer.rescore(self.scorer.score(phrase.yield_scorable())))
			training.append((scored, label))
		self.classifier.find_threshold(training)

	def evaluate(self, training_data, train=False):
		results = {}
		probs   = {}

		if train:
			self.classifier.find_threshold(training_data)

		for phrase, _label in training_data:
			label, score, estimate = self.get_prediction(phrase)
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