import types

from feature_database import FeatureDatabase

from sqlalchemy import Table, Sequence, Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref
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

	__tablename__ = 'sources'

	id = Column(Integer, Sequence('source_id_seq'), primary_key = True)
	source = Column(String, nullable = False, unique = True)

	def __init__(self, source):
		self.source = source

class Example(Base):

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

	def __init__(self, engine):
		"""
			Initializes this feature database using an engine
		"""

		if type(engine) == types.StringType:
			engine = create_engine(engine)
		self._engine = engine
		self._session = Session(bind=self._engine)
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
		session.commit()
		return True

	def get_source(self, qry):
		session = self._get_session()
		for obj in session.query(Source).filter_by(source=qry):
			return obj

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
		session.commit()
		return True

	def get_feature_examples(self, feature, sources=set([])):

		feature_obj = self.get_feature(feature)
		if feature_obj is None:
			return

		session = self._get_session()

		for obj in session.query(Example).filter_by(feature=feature_obj):
			yield obj.source.source, obj.label, obj.extra
