#!/usr/bin/env python

import types

from numpy import complex64
from scipy.fftpack import ifft, fft

from sqlalchemy import Table, Sequence, Column, Integer, create_engine
from sqlalchemy.orm.session import Session 
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.types import PickleType

from scipy.fftpack import ifft, fft

from models import Sentence
from sentences import SentenceClassifier 

Base = declarative_base()

class Feature(Base):

	__tablename__ = 'features'

	id = Column(Integer, Sequence('feature_id_seq'), primary_key = True)
	nonphrase_vector = Column(PickleType, nullable = False)
	phrase_scores    = Column(PickleType, nullable = False)
	phrase_probs     = Column(PickleType, nullable = False)
	label			 = Column(Integer, nullable = False)

	@validates('label')
	def validate_label(self, key, label):
		assert label in [-1, 1]

	@validates('nonphrase_vector')
	def validate_nonphrase_vector(self, key, vector):
		for val in vector:
			assert type(val) == types.StringType 

	@validates('phrase_scores')
	def validate_phrase_scores(self, key, vector):
		for val in vector:
			assert type(val) == types.FloatType
			assert val >= -1.0 and val <= 1.0
	
	@validates('phrase_probs')
	def validate_phrase_scores(self, key, vector):
		for val in vector:
			assert type(val) == types.FloatType
			assert val >= 0.0 and val <= 1.0

	def __init__(self, punc, scores, probs, label):
		self.nonphrase_vector = punc
		self.phrase_scores = scores 
		self.phrase_probs  = probs
		self.label = label

class SentenceFFTClassifier(SentenceClassifier):

	def __init__(self, engine, classifier=None):
		super(SentenceClassifier, self).__init__(classifier)
		self._feature_db = create_engine(engine)
		self._session    = Session(bind=self._feature_db)
		Base.metadata.create_all(self._feature_db)

	def finalize(self):
		self._session.commit()

	def train(self, sentence, label):
		self._validate_sentence(sentence)
		punc = tuple([word for word, pos in sentence.remainder])
		scores, probs = []
		for phrase in sentence.phrases:
			label, score, estimate = self.classifier.get_prediction(phrase)
			scores.append(score)
			probs.append(score)

		f = Feature(punc, scores, probs, label)
		self.session.add(f)

	def _match(self, punc):
		for obj in self._session.query(Feature).filter_by(nonphrase_vector=punc):
			yield obj

	@classmethod
	def _fft_signal(cls, signal, length=None):
		if length is None:
			length = len(signal)

		signal = cls.to_complex(signal)

		if len(signal) % 2 != 0:
			signal = cls.pad_end(signal, 1)

		padding = (abs(len(signal) - length))/2
		print padding, len(signal)
		if padding > 0:
			signal = cls.pad_sim(signal, padding)

		if not len(signal) == length:
			raise ValueError(("Need to be the same length: ", len(signal), length))

		power_pad = cls.next_pow2(len(signal))
		pad_toadd = cls.power_pad - len(signal)

		signal = cls.pad_end(signal, pad_toadd)

		return signal

	def get_prediction(self, sentence):
		punc = tuple([word for word, pos in sentence.remainder])

		scores, probs = []
		for phrase in sentence.phrases:
			label, score, estimate = self.classifier.get_prediction(phrase)
			scores.append(score)
			probs.append(score)

		if len(scores) == 0:
			return 0, 0, None 

		average_prob = sum(probs) / len(probs)

		scores = self._fft_signal(scores)
		probs  = self._fft_signal(probs )

		scores = fft(scores)
		probs  = fft(probs )

		best_correlation, best_label, best_probability = 0, 0, 0
		for f in self._match(punc):
			assert len(f.phrase_scores) == len(scores)

			# Convert to complex
			m_scores = fft(self.to_complex(f.phrase_scores))

			cnv = [i * j.conjugate() for i, j in zip(scores, m_scores)]
			res = ifft(cnv)
			correlation_signal = [r.real for r in res]
			corr = max(correlation_signal)
			if corr > best_correlation:
				best_correlation = corr 
				best_label = f.label 
				m_probs  = fft(self.to_complex(f.phrase_probs))
				cnv = [i * j.conjugate() for i, j in zip(probs, m_probs)]
				res = ifft(cnv)
				correlation_signal = [r.real for r in res]
				best_probability = max(correlation_signal)

		# Work out the average probability of the first
		average_prob *= best_correlation * best_probability

		return best_label, best_correlation*best_label, average_prob



	@classmethod
	def to_complex(cls, arr):
		return [complex64(a) for a in arr]

	@classmethod
	def ccmult(cls, i, j):
		return i * j.conjugate()

	@classmethod
	def pad_sim(cls, arr, amount):
		ret = [0 for i in range(amount)]
		ret += arr 
		ret += [0 for i in range(amount)]
		return ret

	@classmethod
	def pad_end(arr, amount):
		return arr + [0 for i in range(amount)]

	@classmethod
	def next_pow2(cls, of):
		cur = 1
		while cur < of:
			cur *= 2

		return cur 