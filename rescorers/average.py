from rescorer import Rescorer

class AverageRescorer(Rescorer):

	def get_score(self, score):

		if score is None:
			return score

		score_len = len(score)
		score_total_pos = sum([x['pos'] for x in score])
		score_total_neg = sum([x['neg'] for x in score])

		if score_len == 0:
			return None

		score_total_pos /= score_len
		score_total_neg /= score_len

		return {'pos': score_total_pos, 'neg': score_total_neg}