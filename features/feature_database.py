#!/usr/bin/env python

"""
	Abstract class for a feature database
"""

class FeatureDatabase(object):
	
	def __init__(self, name):
		pass

	def feature_exists(self, feature):
		"""
			Searches the database for feature and returns True if it exists,
			False otherwise.
		"""
		pass 

	def add_feature(self, feature):
		"""
			Inserts feature into the database and returns True if successful.
			Returns false otherwise.
		"""
		pass

	def add_feature_example(self, feature, label, source, extra=None):
		"""
			Inserts feature into the database (if it doesn't exist) and associates
			label and extra information with it. Returns True on success.
		"""
		if not self.feature_exists(feature):
			self.add_feature(feature)

	def get_sources(self):
		"""
			Returns a set containing sources stored within this FeatureDatabase
		"""

	def get_feature_examples(self, feature, sources=None):
		"""
			Returns a generator which can be used to iterate through training
			examples. 
		"""
		pass

	def finalize(self):
		"""
			Implementors have DB-specific methods to do clearup.
		"""
		pass