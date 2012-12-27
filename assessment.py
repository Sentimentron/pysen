#!/usr/bin/env python

"""
	assessement.py helps to compare different approaches
	to labelling sentences and documents.
"""

from readers.pang_lee import *
import itertools

def compute_precision(true_positives, false_positives):
	return true_positives * 1.0 / (true_positives + false_positives)

def compute_recall(true_positives, other_positives):
	"""
	Recall in this context is defined as the number of true positives divided by the total number of elements that actually belong to the positive class (i.e. the sum of true positives and false negatives, which are items which were not labeled as belonging to the positive class but should have been).
	"""
	return true_positives / (true_positives + other_positives)

def pl_assess_sentence_performance(label_func, sbase, interactive=False):
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

		if interactive:
			print sentence, label, result
			raw_input("Press any key")
		
		if result == 0:
			continue

		classified += 1
		if result == label:
			accurate += 1
			print total, "%.2f\t%.2f" % (100.0*accurate/classified, 100.0*classified/total)

	precision = compute_precision(len(result_junk[(1, 1)]), len(result_junk[(-1, 1)]))
	recall = compute_precision(len(result_junk[(1, 1)]), len(result_junk[(1, -1)]))
	print "precision (positive): %.2f%%" % (100.0*precision)
	print "recall (positive): %.2f%%" % (100.0*recall)

	return {"results": result_junk, "precision": precision, 
				"recall": recall, "accuracy": 1.0*accurate/classified, 
				"coverage": 1.0*classified/total, "total": total, 
				"classified": classified, "accurate": accurate}



