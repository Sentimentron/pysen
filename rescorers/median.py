from rescorer import Rescorer

class MedianRescorer(Rescorer):
	
	def get_score(self, scores):

		if scores is None:
			return None

		score_pos = sorted([x['pos'] for x in scores])
		score_neg = sorted([x['neg'] for x in scores])

		mid_pos = len(score_pos) / 2
		mid_neg = len(score_neg) / 2

		return {'pos': score_pos[mid_pos], 'neg': score_neg[mid_neg]}
