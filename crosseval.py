#!/usr/bin/env python

import random

class CrossFoldValidationFramework(object):

	def __init__(self, training_data, num_folds=5):
		random.shuffle(training_data)
		fold_counter = 0
		self.folds = []
		self.data  = []
		while fold_counter < num_folds:
			fold_counter += 1
			start = (fold_counter-1)*(len(training_data)/num_folds)
			end   = (fold_counter  )*(len(training_data)/num_folds)
			self.folds.append(training_data[start:end])

	def get_training_data(self, fold_no):
		num_folds = len(self.folds)
		ret = []
		for i in range(num_folds):
			if i == fold_no:
				continue
			for r in self.folds[i]:
				ret.append(r)
		return ret 

	def get_evaluation_data(self, fold_no):
		return self.folds[fold_no]

	def accumulate_eval_data(self, data):
		for key in data:
			if key not in self.data:
				self.data[key] = []
			self.data[key].append(data)