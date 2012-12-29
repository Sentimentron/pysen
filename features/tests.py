import sys
from sqlite_database import SQLiteFeatureDatabase

db_file = ":memory:"

def delete_test_db():
	if db_file != ":memory:":
		import os 
		if os.path.exists(db_file):
			os.remove(db_file)
		else:
			return False
	return True 

def create_test_db():
	fdb = SQLiteFeatureDatabase(db_file)
	return True

def invalid_feature_example_test():
	fdb = SQLiteFeatureDatabase(db_file)
	try:
		return fdb.add_feature_example("invalid_feature", 5)
	except ValueError as ex:
		return True 
	return False 

def valid_feature_example_test():
	fdb = SQLiteFeatureDatabase(db_file)
	return fdb.add_feature_example("valid_feature", 1)

def get_feature_examples():
	fdb = SQLiteFeatureDatabase(db_file)
	fdb.add_feature_example("valid_feature", -1)
	fdb.add_feature_example("another_valid_feature", 1)
	fdb.add_feature_example("another_valid_feature", -1, "default", {'distrust': True})
	fdb.add_feature_example("something_else", 1)

	for label, extra in fdb.get_feature_examples("another_valid_feature"):
		print label, extra

all_tests = [

	("--delete", delete_test_db),
	("--create", create_test_db),
	("--invalid", invalid_feature_example_test),
	("--valid", valid_feature_example_test),
	("--specific", get_feature_examples)

]

if __name__ == "__main__":

	if "--memory" not in sys.argv:
		db_file = "test.db"

	if "--all" not in sys.argv:
		tests = filter(lambda y: y[0] in sys.argv, all_tests)
	else:
		tests = all_tests

	if len(tests) == 0:
		print >> sys.stderr, "Need some tests:"
		for arg, func in all_tests:
			print >> sys.stderr, "\t", arg 
		sys.exit(1)

	for arg, test in tests:
		ex = None 
		result = test()
		print "%-15s" % arg, 
		if result:
			print "PASS"
		else:
			print "FAIL"
			if ex is not None:
				raise ex


