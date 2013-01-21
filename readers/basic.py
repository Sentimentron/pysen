#!/usr/bin/env python

import cStringIO
import csv

def from_file(fp):

	cst = cStringIO.StringIO()
	# Copy input
	for line in fp:
		cst.write(line)

	cst.seek(0)
	red = csv.reader(cst, quotechar='"')
	for line in red:
		try:
			label, sentence = line
		except ValueError:
			label = line[0]
			sentence = ','.join(line[1:])
		yield int(label), sentence