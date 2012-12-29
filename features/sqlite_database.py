#!/usr/bin/env python

"""
	SQLite3 based feature database used by classifiers
"""

import sqlite3
import pickle

from feature_database import FeatureDatabase

FEATURE_EX_PREFIX="feature_ex_"

class SQLiteFeatureDatabase(FeatureDatabase):

	def _get_tables(self):
		ret = set([])
		with self._get_connection() as con:
			cur = con.cursor()
			cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
			for row in cur:
				ret.add(row[0])
			cur.close()
		return ret 

	def _get_connection(self, isolation="DEFERRED"):
			return sqlite3.connect(self._file, isolation_level=isolation)

	def _master_table_exists(self):
		tables = self._get_tables()
		if "feature_m" in tables:
			return True 
		return False

	def _gen_feature_table_name(self, name):
		return FEATURE_EX_PREFIX+name 

	def _gen_name_from_ftable_name(self, name):
		return name[len(FEATURE_EX_PREFIX):]

	def _create_master_table(self):
		sql = """
			CREATE TABLE feature_m (id INTEGER PRIMARY KEY, feature BLOB UNIQUE NOT NULL);
		"""
		with self._get_connection("EXCLUSIVE") as con:
			cur = con.cursor()
			cur.execute(sql)
			con.commit()
			cur.close()
			return True 
		return False 

	def _feature_table_exists(self, name):
		tname = self._gen_feature_table_name(name)
		tables = self._get_tables()
		if tname in tables:
			return True 
		return False 

	def _get_pickled_feature(self, feature):
		return pickle.dumps(feature)

	def _get_unpickled_feature(self, pickled_feature):
		return sqlite3.Binary(pickle.loads(pickled_feature))

	def _get_feature_id(self, feature):
		pf = self._get_pickled_feature(feature)
		ret = None
		with self._get_connection() as con:
			cur = con.cursor()
			sql = "SELECT id FROM feature_m WHERE feature = ?"
			cur.execute(sql, (pf,))
			for row in cur:
				ret = row[0]
			cur.close()
		return ret 

	def _create_feature_table(self, name):
		name = self._gen_feature_table_name(name)
		with self._get_connection("EXCLUSIVE") as conn:
			cur = conn.cursor()
			sql = """CREATE TABLE """+name+ """ (
					id INTEGER PRIMARY KEY,
					feature_id INTEGER,
					label INTEGER,
					extra BLOB,
					FOREIGN KEY (feature_id) REFERENCES feature_m(id)
				)"""
			cur.execute(sql)
			cur.close()
			conn.commit()


	def feature_exists(self, feature):
		if self._get_feature_id(feature) is not None:
			return True
		return False

	def add_feature(self, feature):
		# Get the pickled feature
		feature = self._get_pickled_feature(feature)

		# Construct query
		sql = "INSERT INTO feature_m (feature) VALUES (?)"

		# Execute query
		with self._get_connection() as con:
			cur = con.cursor()
			cur.execute(sql, [feature])
			con.commit()

		return True

	def add_feature_example(self, feature, label, source="default", extra=None):

		super(SQLiteFeatureDatabase, self).add_feature_example(feature, label, source, extra)

		# Check if the feature_source table exists 
		if not self._feature_table_exists(source):
			self._create_feature_table(source)

		# Check the label
		if label not in [0, 1]:
			raise ValueError("label: must be between 0 and 1")

		# Get the feature identity
		feature_id = self._get_feature_id(feature)

		# Get the pickled feature
		feature = self._get_pickled_feature(feature)

		# Get the pickled extra stuff
		if extra is not None:
			extra = pickle.dumps(extra)

		# Get the table name
		source = self._gen_feature_table_name(source)

		# Insert the feature
		sql_extra = "INSERT INTO %s (feature_id, label, extra) VALUES (?, ?, ?)" % (source,)
		sql_normal = "INSERT INTO %s (feature_id, label) VALUES (?, ?)" % (source,)
		with self._get_connection() as con:
			cur = con.cursor()
			if extra is not None:
				cur.execute(sql_extra, [feature_id, label, sqlite3.Binary(extra)])
			else:
				cur.execute(sql_normal, [feature_id, label])
			con.commit()

		return True 

	def get_sources(self):
		tables = self._get_tables()
		tables = filter(lambda x: "feature_m" not in x, tables)
		sources = map(self._gen_name_from_ftable_name, tables)
		sources = set(sources)
		return sources

	def get_feature_examples(self, feature, sources=None):
		
		# Figure out which tables we need to query
		example_tables = filter(lambda x: "feature_m" not in x, self._get_tables())
		tables = []
		if sources is not None:
			# Map the sources onto table names
			sources = map(self._gen_feature_table_name, sources)
			for source in sources:
				source_tab = self._gen_feature_table_name(source)
				if source_tab not in example_tables:
					raise ValueError("sources: must exist within database - %s", (source,))
				tables.add(source_tab)
		else:
			tables = example_tables

		# Figure out the id of the thing we're querying
		feature_id = self._get_feature_id(feature)
		if feature_id is None:
			return

		# Open the connection and cursor and generate the results
		with self._get_connection() as con:
			cur = con.cursor()
			# Query each of the example tables 
			for table in tables:
				sql = "SELECT label, extra FROM %s WHERE feature_id = ?" % (table,)
				cur.execute(sql, [feature_id])
				for row in cur:
					label, extra = row 
					if extra is not None:
						extra = pickle.loads(extra)
					yield (label, extra)
			cur.close()


	def __init__(self, db_file=":memory:"):

		self._file = db_file

		# Find out whether the sqlite database already contains
		# the feature and training database tables. 

		if not self._master_table_exists():
			self._create_master_table()