#!/usr/bin/env python


import random
import types

from feature_database import FeatureDatabase

class TrainingSimulationFeatureDatabase(FeatureDatabase):

	"""
		This database wraps another FeatureDatabase and restricts its
		output to a specified level. Used to simulate the effects of
		training.
	"""

	def __init__(self, coverage):
		if type(coverage) is not types.FloatType:
			raise TypeError("coverage: must a float")

		if coverage > 1 or coverage < 0:
			raise TypeError("coverage: must be between 0 and 1")

		self.coverage = coverage
		self.features = None 

	def set_features(self, features):
		self.features = []
		for feature in features:
			if self._coverage_check():
				self.features.append(feature)

	def feature_exists(self, feature):
		for f, label, extra in self.features:
			if feature == f:
				return True 
		return False

	def _coverage_check(self):
		r = random.random()
		return self.coverage > r

	def add_feature(self, feature):
		raise NotImplementedError("add_feature: not supported for this FeatureDatabase")

	def add_feature_example(self, feature, label, source, extra = None):
		raise NotImplementedError("add_feature_example: not supported for this FeatureDatabase")

	def get_sources(self):
		return set([])

	def get_feature_examples(self, feature, sources=None):
		for f, label, extra in self.features:
			if feature == f:
				yield label, extra

	def get_all_features(self):
		for thing in self.features:
			yield thing