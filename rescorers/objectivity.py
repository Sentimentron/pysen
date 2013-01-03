from rescorer import Rescorer

class ObjectivityRescorer(Rescorer):

	def get_score(self, score):
		if score is None:
			return None

		pos_score = score['pos']
		neg_score = score['neg']

		objectivity = 1 - (pos_score+neg_score)
		return objectivity