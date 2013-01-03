from rescorer import Rescorer

class MaximumRescorer(Rescorer):
	
	def get_score(self, scores):

		if scores is None:
			return scores

		score_pos = max([x['pos'] for x in scores])
		score_neg = max([x['neg'] for x in scores])

		return {'pos': score_pos, 'neg': score_neg}
