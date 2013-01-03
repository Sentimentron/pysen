from rescorer import Rescorer

class MedianRescorer():
	
	def get_score(self, scores):

		score_pos = sorted([x['pos'] for score in scores])
		score_neg = sorted([x['neg'] for score in scores])

		return {'pos': score_pos, 'neg': score_neg}
