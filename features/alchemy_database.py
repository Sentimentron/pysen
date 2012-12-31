import types

from feature_database import FeatureDatabase

from sqlalchemy import Table, Sequence, Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import PickleType

Base = declarative_base()

class Feature(Base):

	"""
		Features are individual words and various other bits and bobs
	"""

	__tablename__ = 'features'

	id = Column(Integer, Sequence('feature_id_seq'), primary_key = True)
	feature = Column(PickleType, unique = True, nullable = False)

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
	extra = Column(PickleType, nullable = True)

	def __init__(self, feature, label, source, extra):
		self.feature = feature
		self.source = source
		self.label = label
		self.extra = extra


class AlchemyFeatureDatabase(FeatureDatabase):

	"""
		Uses SQLAlchemy to provide a a FeatureDatabase backed by an SQL database.
		IMPORTANT: all insertions must be followed by a finalize() call
	"""

	def __init__(self, engine):
		"""
			Initializes this feature database using an engine
		"""

		if type(engine) == types.StringType:
			engine = create_engine(engine)
		self._engine = engine
		self._session = Session(bind=self._engine)
		self._cache = None
		self._cache_dirty = False
		self.initialize()

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
		return True

	def get_feature(self, qry):
		session = self._get_session()
		for obj in session.query(Feature).filter_by(feature=qry):
			return obj

	def add_source(self, source):
		session = self._get_session()
		source = Source(source)
		session.add(source)
		return True

	def get_source(self, qry):
		session = self._get_session()
		for obj in session.query(Source).filter_by(source=qry):
			return obj

	def _gen_cache(self):
		self._cache = {}
		cache = self._cache
		session = self._get_session()
		for obj in session.query(Example)\
			.options(joinedload('feature'))\
			.options(joinedload('source')):
			if obj.source.source not in cache:
				cache[obj.source.source] = {}
			sub_cache = cache[obj.source.source]
			feature = obj.feature.feature 
			if type(feature) is not types.StringType:
				sub_cache_key = str(obj.feature.feature)
			else:
				sub_cache_key = feature
			if sub_cache_key not in sub_cache:
				sub_cache[sub_cache_key] = [(obj.label, obj.extra)]
			else:
				sub_cache[sub_cache_key].append((obj.label, obj.extra))
		self._cache_dirty = False


	def add_feature_example(self, feature, label, source=None, extra = None):

		if source is None:
			source = "default"

		if label not in [-1, 1]:
			raise ValueError("label: must be -1 or 1")

		source_obj = self.get_source(source)
		feature_obj = self.get_feature(feature)

		if source_obj is None:
			self.add_source(source)
			return self.add_feature_example(feature, label, source, extra)
		if feature_obj is None:
			self.add_feature(feature)
			return self.add_feature_example(feature, label, source, extra)

		session = self._get_session()

		example_obj = Example(feature_obj, label, source_obj, extra)

		session.add(example_obj)
		self._cache_dirty = True
		return True

	def get_feature_examples(self, feature, sources=None):

		if self._cache is None or self._cache_dirty:
			self._gen_cache()

		if type(feature) is not types.StringType:
			feature = str(feature)

		for source in self._cache:
			if sources is not None:
				if source not in sources:
					continue
			sc = self._cache[source]
			if feature not in sc:
				continue 
			for pair in sc[feature]:
				yield pair 