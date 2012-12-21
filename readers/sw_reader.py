from models import SWEntry, SWEntryCollection

def read_sen_file(fp):

	ret = {}

	for line in fp:
		if len(line) == 0:
			return 0
		if line[0] == "#":
			continue

		fields = line.split('\t')
		fields = map(lambda x: x.strip(), fields)
		if len(filter(lambda x: len(x) == 0, fields)) > 0:
			 continue
		pos, identifier, pos_score, neg_score, terms, gloss = fields # = line.split('\t')

		pos_score = float(pos_score)
		neg_score = float(neg_score)

		if pos_score == 0 and neg_score == 0:
			pass

		for term in terms.split(' '):
			term, spatula, no = term.partition('#')
			term = term.strip()
			entry = {'pos': pos_score, 'neg': neg_score, 'partofspeech': pos, 'no': no}
			#entry = SWEntry(pos_score, neg_score, pos, no)
			if term in ret:
				ret[term].append(entry)
			else:
				ret[term] = [entry]

	return ret