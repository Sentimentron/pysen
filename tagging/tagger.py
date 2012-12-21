class Tagger(object):
	"""
		A tokenizer breaks a sentence in part-of-speech tags, and 
		can additionally provide pre-processing and normalization.
	"""
	def __init__(self):
		pass
	
	def tag(self, text, collator):
		"""
			Takes a natural-language sentence and returns a POS tagged version.
		"""
		pass

	def push_to_collation(self, collator, item, result):
		collator.push(self, item, "TAG", result)