from rescorer import Rescorer

class AverageRescorer(Rescorer):

	def get_score(self, score):

		if score is None:
			return score

		score_len = len(score)
		score_total_pos = sum([x['pos'] for x in score])
		score_total_neg = sum([x['neg'] for x in score])
		score_total = score_total_pos - score_total_neg

		if score_len == 0:
			return None
			
		return 1.0 * score_total / score_len