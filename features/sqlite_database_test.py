import sys
from sqlite_database import SQLiteFeatureDatabase

db_file = ":memory:"

tests = [

	("--delete", delete_test_db),
	("--create", create_test_db)

]

def delete_test_db():
	if db_file != ":memory:":
		import os 
		os.remove(db_file)

def create_test_db():
	fdb = SQLiteFeatureDatabase(db_file)

if __name__ == "__main__":

	if "--memory" not in sys.argv:
		db_file = "test.db"

	if "--all" not in sys.argv:
		tests = filter(lambda y: y[0] in sys.argv, tests)

	if len(tests) == 0:
		print >> sys.stderr, "Need some tests:"
		for arg, func in tests:
			print >> "\t", arg 

	for arg, test in tests:
		test()

