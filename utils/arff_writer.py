#!/usr/bin/env python

import csv

class ARFFAttribute(object):

	def __init__(self, name, kind):
		self.name = name
		self.kind = kind

	def __str__(self):
		return "@attribute " + self.name + " " + self.kind

	def __repr__(self):
		return "%s:%s(%s)" % (str(type(self)), self.kind, self.name)

class ARFFNumericAttribute(ARFFAttribute):
	
	def __init__(self, name):
		super(ARFFNumericAttribute, self).__init__(name, "numeric")

class ARFFDiscreteAttribute(ARFFAttribute):
	
	def __init__(self, name, values):
		super(ARFFDiscreteAttribute, self).__init__(name, "discrete")
		self.values = set([])
		for val in values:
			self.values.add(val)

	def __str__(self):
		return "@attribute " + self.name + " {" + ','.join(map(str,self.values)) + "}"

class ARFFWriter(object):

	"""
		Outputs to an ARFF file for ad-hoc analysis
	"""

	def __init__(self, filename, relation):

		self.relation = relation
		self.filename = filename
		self.attributes = []
		self.data = []

	def push_attribute(self, attr):
		if not isinstance(attr, ARFFAttribute):
			raise TypeError()

		self.attributes.append(attr)

	def push_row(self, row):
		# print row
		if len(row) != len(self.attributes):
			raise ValueError((len(row), len(self.attributes)))
		# assert len(filter(lambda x: x == None, row)) == 0	
		revised = []
		for thing in row:
			if thing is None:
				revised.append("?")
			else:
				revised.append(thing)
		self.data.append(revised)

	def write(self):
		"""
			Writes to filename
		"""
		# Open output file
		fp = open(self.filename, 'w')

		# 
		# Print header
		#
		print >> fp, "@relation", self.relation

		for attr in self.attributes:
			print >> fp, attr 

		print >> fp, ""
		print >> fp, "@data"

		fp.close()

		# Print the data as csv
		fp = open(self.filename, 'a')
		writer = csv.writer(fp)

		for row in self.data:
			writer.writerow(row)

		fp.close()