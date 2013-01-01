def read_AFINN_file(fp):

	ret = {}
	for line in fp:

		fields = line.split('\t')
		fields = map(lambda x: x.strip(), fields)

		if len(filter(lambda x: len(x) == 0, fields)) > 0:
			continue

		word = fields[0]
		score = float(fields[1])
		score_dict = {'pos': 0, 'neg': 0}
		if score < 0:
			score_dict['neg'] = abs(score)/5.0
		elif score > 0:
			score_dict['pos'] = score/5.0

		ret[word] = score 

	return ret