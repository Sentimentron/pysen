#!/usr/bin/env python

from collections import Counter
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
		self.cache = Counter()

	def set_features(self, features):
		self.features = []
		for feature in features:
			if self._coverage_check():
				self.features.append(feature)
		self._gen_cache()

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

	def _gen_cache(self):
		self.cache = Counter()
		for feature, label, extra in self.features:
			self.cache.update([(feature, label)])
		self.features = None

	def get_feature_examples(self, feature, sources=None):
		keys = [(feature, 1), (feature, -1)]
		for key in keys:
			count = self.cache[key]
			feature, label = key 
			for i in range(count):
				yield label, {}


	def get_all_features(self):
		for key in self.cache:
			count = self.cache[key]
			feature, label = key 
			for i in range(count):
				yield feature, label, key