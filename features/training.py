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

	def __init__(self, fdb, coverage):
		if not isisnstance(fdb, FeatureDatabase):
			raise TypeError("fdb: must derive from FeatureDatabase")

		if type(coverage) is not types.FloatType:
			raise TypeError("coverage: must a float")

		if coverage > 1 or coverage < 0:
			raise TypeError("coverage: must be between 0 and 1")

		self.wrapping = fdb
		self.coverage = coverage


	def _coverage_check(self):
		r = random.random()
		return self.coverage > r

	def feature_exists(self, feature):
		if not self._coverage_check():
			return False 

		return self.wrapping.feature_exists(feature)

	def add_feature(self, feature):
		raise NotImplementedError("add_feature: not supported for this FeatureDatabase")

	def add_feature_example(self, feature, label, source, extra = None):
		raise NotImplementedError("add_feature_example: not supported for this FeatureDatabase")

	def get_sources(self):
		return self.wrapping.get_sources()

	def get_feature_examples(self, feature, sources=None):
		all_examples = self.wrapping.get_feature_examples(feature, sources)
		for example in all_examples:
			if not self._coverage_check():
				continue
			yield example