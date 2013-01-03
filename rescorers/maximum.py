from rescorer import Rescorer

class MaxRescorer():
	
	def get_score(self, scores):

		score_pos = max([x['pos'] for score in scores])
		score_neg = max([x['neg'] for score in scores])

		return {'pos': score_pos, 'neg': score_neg}
