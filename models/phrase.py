class Phrase(object):

	def __init__(self, sentence=None):
		self.keywords = set([])
		self.words = set([])
		self.wordlist = []

		if sentence is not None:
			for word, pos, norm in sentence:
#				print word, pos
				self.add_word(word, pos)

	@classmethod
	def _check_pos(cls, pos, strict=False):
		allowed = ["RB", "NN", "JJ", "VB"]
		tolerated = ["DT", "PRP", "POS", "IN", "MD", "EX", "TO"]
		
		for _pos in allowed:
			if _pos in pos:
				return True

		if not strict:
			for _pos in tolerated:
				if _pos in pos:
					return True 

		return False 

	@classmethod
	def _check_word(self, word):
		for _char in word:
			if not (_char <= 'z' and _char >= 'a'):
				if _char != "-":
					return False 
		return True

	@classmethod 
	def _proc_hyphenated(self, word):
		word = word.encode("ascii", "ignore")
		if "-" not in word:
			return [word]
		return word.split("-")

	def add_word(self, word, pos):
		if not self._check_pos(pos):
			raise ValueError(("Not allowed in a phrase", word, pos))

		if self._check_pos(pos, True):
			if self._check_word(word):
				self.words.add((word, pos))

		self.wordlist.append(word)

	def get_text(self):
		return ' '.join(self.wordlist)

	def score(self, scorer, rescorer):
		scores = []
		for word, pos in self.words:
			score = scorer.get_score(word, pos)
			if score is None:
				score = scorer.get_score(word)
			if score is not None:
				scores.append((word, pos, word, scorer.get_score(word, pos)))
		scores = list(rescorer.rescore(scores))
		count  = len(scores)
		if count == 0:
			return 0
		total = 0
		for word, pos, norm, score in scores:
			total += score['pos']
			total -= score['neg']
		return total*1.0/count

	def yield_scorable(self):
		for word, pos in self.words:
			yield word, pos, word

	def __str__(self):
		return "Phrase(%s)" % (str(self.words), )

	def __iter__(self):
		return self.words.__iter__()