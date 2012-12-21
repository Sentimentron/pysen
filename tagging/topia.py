from tagger import Tagger 

class TopiaTagger(Tagger):
	"""
		Uses topia.termextract's tagger to process a sentence. 
		This should be the default pysen Tagger. 
	"""

	def __init__(self):
		self.tagger = tag.Tagger()
		self.tagger.initialize()


	def tag(self, text, collator):
		return self.tagger(text)
