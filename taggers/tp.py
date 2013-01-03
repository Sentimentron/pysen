from tagger import Tagger
from topia.termextract import tag

class TopiaTagger(Tagger):
	"""
		Uses topia.termextract's tagger to process a sentence. 
		This should be the default pysen Tagger. 
	"""

	def __init__(self):
		self.tagger = tag.Tagger()
		self.tagger.initialize()


	def tag(self, text):
		tagged = self.tagger(text)
		ret = []
		for word, pos, norm in tagged:
			if "\n" in word:
				word = word.replace("\n", "")
			ret.append((word, pos, norm))
		return ret

class ExpandingTopiaTagger(TopiaTagger):

	def tag(self, sentence):
		construct = []
		for word in sentence.split(' '):
			if "'" in word:
				if word == "it's":
					word = "it is"
				elif word == "you'd":
					word = "you would"
				elif word == "can't":
					word = "cannot"				
				elif "'ll" in word:
					word = word[0:-3] + " will"
				elif "'re" in word:
					word = word[0:-3] + " are"
				elif "n't" in word:
					word = word[0:-3] + " not"
			construct.append(word)
		super(ExpandingTopiaTagger, self).tag(' '.join(construct))