#!/usr/bin/env python

"""
	assessement.py helps to compare different approaches
	to labelling sentences and documents.
"""

from readers.pang_lee import *
import itertools

def pl_assess_sentence_performance(label_func, sbase):
	"""
		Runs label_func on every sentence within pang/lee's 
		dataset and prints the results as we go along. 
			label_func: a function which returns label 
				as part of a tuple. The second part of the tuple
				is returned as part of a list when this function
				ends. 
			sbase: the prefix of the documents containing the
				sentences
	"""

	result_junk = {combo : [] for combo in itertools.product([-1, 0,1], [-1, 0,1])}

	classified, accurate, total = 0, 0, 0

	for sentence, label in get_sentence_pairs(sbase):

		total += 1
		result, junk = label_func(sentence)

		result_junk[(label, result)].append(junk)

		if result == 0:
			continue

		classified += 1
		if result == label:
			accurate += 1
			print total, "%.2f\t%.2f" % (100.0*accurate/classified, 100.0*classified/total)

	return result_junk



