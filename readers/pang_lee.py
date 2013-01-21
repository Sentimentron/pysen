#!/usr/bin/env python

# Reader for Pang/Lee's datasets

import os

def yield_sentiment_pairs(sentences, pos):
	res = 0
	for sentence in sentences:
		if pos.strip() == 'pos':
			res = 1
		else:
			res = -1
		yield(sentence, res)

def _yield_dir_entries(directory):
	for dirname, dirnames, filenames in os.walk(directory):
	    for subdirname in dirnames:
	        yield os.path.join(dirname, subdirname)
	    for filename in filenames:
	        yield os.path.join(dirname, filename)

def _yield_not_dir_entries(genr):
	for fname in genr:
		if not os.path.isdir(fname):
			yield fname

def get_sentence_pairs(sentence_base):
	
	# Open the positive and negative polarity files
	fps = [(open(sentence_base+sen,"rt"), sen) for sen in ["pos","neg"]]

	# Read the contents of each of the files
	contents = [(fp.read(), sen) for fp, sen in fps]

	for lines, sentiment in contents:
		
		sentences = lines.split('\n')
		
		if sentiment == 'neg':
			sentiment = -1
		else:
			sentiment = 1

		for sentence in sentences:
			# Walk back through the sentence and strip
			# the last full-stop
			stop = -1
			for position, _char in enumerate(sentence):
				if _char == '.':
					stop = position 

			if stop != -1:
				sentence = sentence[0:stop]
			
			if len(sentence.strip()) > 0:
				yield sentence, sentiment

def yield_document_pairs(document_base):

	# Get the positive / negative filenames
	fnames = _yield_not_dir_entries(_yield_dir_entries(document_base))

	# Yield string, label pairs
	for fname in fnames:
		# Read the document body
		fp  = open(fname, 'r')
		txt = fp.read().decode('utf-8')
		fp.close()

		# Decide the original label
		label = 0
		if "pos/" in fname:
			label =  1
		elif "neg/" in fname:
			label = -1

		assert label in [1, -1]

		# Output
		yield (fname, txt, label)
