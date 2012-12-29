#!/usr/bin/env python

"""
	SQLite3 based feature database used by classifiers
"""

import sqlite3
import pickle

from feature_database import FeatureDatabase

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
		return "feature_ex_"+name 

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
		return pickle.loads(pickled_feature)

	def _get_feature_id(self, feature):
		pf = self._get_unpickled_feature(feature)
		ret = None
		with self._get_connection() as conn:
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
				) CONSTRAINT FOREIGN KEY (feature_id) REFERENCES feature_m(id)"""
			cur.execute(sql)
			cur.close()
			conn.commit()


	def feature_exists(self, feature):
		if self._get_feature_id(feature) is not None:
			return True
		return False

	def add_feature_example(self, feature, label, source="default", extra=None):

		super(SQLiteFeatureDatabase, self).add_feature_example(feature, label, source, extra)

		# Check if the feature_source table exists 
		if not self._feature_table_exists(source):
			self._create_feature_table(source)

		# Get the feature identity
		feature_id = self._get_feature_id(feature)

		# Get the pickled feature
		feature = self._get_pickled_feature(feature)

		# Get the pickled extra stuff
		if extra is not None:
			extra = pickle.dumps(extra)

		# Get the table name
		source = self._gen_feature_table_name(source)

		sql_extra = "INSERT INTO %s (feature_id, label, extra) VALUES (?, ?, ?)" % (source,)
		sql_normal = "INSERT INTO %s (feature_id, label) VALUES (?, ?)" % (source,)
		with self._get_connection() as con:
			cur = con.cursor()
			if extra is not None:
				cur.execute(sql_extra, [])


	def __init__(self, db_file=":memory:"):

		self._file = db_file

		# Find out whether the sqlite database already contains
		# the feature and training database tables. 

		if not self._master_table_exists():
			self._create_master_table()