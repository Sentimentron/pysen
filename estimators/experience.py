import types
from collections import Counter	
from sqlalchemy import Table, Sequence, Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, joinedload, validates
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Feature(Base):

	__tablename__ = 'features'

	id = Column(Integer, Sequence('feature_id_seq'), primary_key = True)
	feature = Column(String, unique = True, nullable = False)

	def __init__(self, feature):
		self.feature = feature

class Source(Base):
	"""
		Sources are the training files where features come from.
	"""

	__tablename__ = 'sources'

	id = Column(Integer, Sequence('source_id_seq'), primary_key = True)
	source = Column(String, nullable = False, unique = True)

	def __init__(self, source):
		self.source = source

class Example(Base):
	"""
		Examples are individual good/bad labels associated with Features, 
		observed in Sources
	"""

	__tablename__ = 'examples'

	id = Column(Integer, Sequence('example_id_seq'), primary_key = True)
	source_id = Column(Integer, ForeignKey("sources.id"), nullable = False)
	feature_id = Column(Integer, ForeignKey("features.id"), nullable = False)
	source = relationship("Source", backref=backref('examples', order_by=id))
	feature = relationship("Feature", backref=backref('examples', order_by=id))
	label = Column(Integer, nullable = False)
	count = Column(Integer, nullable=False, default=0)

	@validates('count')
	def _validate_count(self, key, count):
		assert count >= 0
		return count

	def __init__(self, feature, label, source, count):
		self.feature = feature
		self.source = source
		self.label = label
		self.count = count

class WordLabelDatabase(object):

	def __init__(self, engine):
		if type(engine) == types.StringType:
			new_engine = create_engine(engine)
			if "sqlite:" in engine:
				new_engine.raw_connection().connection.text_factory = str
			engine = new_engine 
		self._engine = engine
		self._session = Session(bind=self._engine)
		self._cache = None
		self._cache_dirty = True
		self.initialize()

	def _generate_cache(self):
		self._cache = {}
		cache = self._cache 
		session = self._get_session()
		for obj in session.query(Example)\
			.options(joinedload('feature')):
			cache_key = obj.feature.feature 
			if cache_key not in cache:
				cache[cache_key] = {}
			cache[cache_key][obj.label] = obj.count

		self._cache_dirty = False

	def get_feature_labels(self, word):
		if self._cache_dirty:
			self._generate_cache()
		if word not in self._cache:
			return None
		return self._cache[word]

	def initialize(self):
		Base.metadata.create_all(self._engine)

	def finalize(self):
		self._session.commit()

	def _get_session(self):
		return self._session 

	def add_feature(self, feature):
		session = self._get_session()
		feature = Feature(feature)
		session.add(feature)

	def get_feature(self, qry):
		session = self._get_session()
		for obj in session.query(Feature).filter_by(feature=qry):
			return obj

	def feature_exists(self, feature):
		qry = self.get_feature(feature)
		return qry != None

	def add_source(self, source):
		session = self._get_session()
		source = Source(source)
		session.add(source)
		return True

	def add_feature(self, feature, label, count_incr=1, source="default"):
		
		session = self._get_session()
		self._cache_dirty = True
		
		# Get the feature
		feature_obj = None
		for obj in session.query(Feature).filter_by(feature=feature):
			feature_obj = obj 
			break

		if feature_obj is None:
			feature_obj = Feature(feature)
			session.add(feature_obj)

		# Resolve source
		source_obj = None
		for obj in session.query(Source).filter_by(source=source):
			source_obj = obj 
			break 

		if source_obj is None:
			source_obj = Source(source)
			session.add(source_obj)

		example_obj = None
		for obj in session.query(Example).filter_by(source=source_obj)\
			.filter_by(feature=feature_obj).filter_by(label=label):
			example_obj = obj 
			break 

		if example_obj is None:
			example_obj = Example(feature_obj, label, source_obj, count_incr)
			session.add(example_obj)
		else:
			example_obj.count += count_incr

	def get_source(self, qry):
		session = self._get_session()
		for obj in session.query(Source).filter_by(source=qry):
			return obj

class WordExperienceEstimator(object):

	def __init__(self, engine):
		
		self.db = WordLabelDatabase(engine)
		self.db._generate_cache()

	def train(self, word, label):
		self.db.add_feature(word, label)

	def flush(self):
		self.db.finalize()

	def get_estimate_fromscore(self, word, score):
		label = 0
		if score is None:
			return 0
		score = score['pos'] - score['neg']
		if score > 0:
			label = 1
		else:
			label = -1

		return self.get_estimate(word, label)

	def get_estimate(self, word, label):
		
		result = self.db.get_feature_labels(word)
		
		if result is None:
			return 0
		
		for key in [-1, 0, 1]:
			if key not in result:
				result[key] = 0

		total_matching, total = 0, 0
		for key in result:
			if key == label:
				total_matching = result[key]
			total += result[key]

		return total_matching * 1.0 / total

