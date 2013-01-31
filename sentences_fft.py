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
		if label not in [-1, 1]:
			raise ValueError(("label", label))
		return label

	@validates('nonphrase_vector')
	def validate_nonphrase_vector(self, key, vector):
		assert len(vector) > 0
		for val in vector:
			assert type(val) == types.StringType 
		return vector

	@validates('phrase_scores')
	def validate_phrase_scores(self, key, vector):
		assert len(vector) > 0
		for val in vector:
			if type(val) is not types.FloatType and type(val) is not types.IntType:
				raise TypeError((val, type(val)))
			assert val >= -1.0 and val <= 1.0
		return vector
	
	@validates('phrase_probs')
	def validate_phrase_probs(self, key, vector):
		assert len(vector) > 0
		for val in vector:
			assert type(val) == types.FloatType or type(val) == types.IntType
			assert val >= 0.0 and val <= 1.0
		return vector

	def __init__(self, punc, scores, probs, label):
		self.nonphrase_vector = punc
		self.phrase_scores = scores 
		self.phrase_probs  = probs
		self.label = label

class SentenceFFTClassifier(SentenceClassifier):

	def __init__(self, engine, classifier=None):
		super(SentenceFFTClassifier, self).__init__(classifier)
		self._feature_db = create_engine(engine)
		self._session    = Session(bind=self._feature_db)
		Base.metadata.create_all(self._feature_db)

	def finalize(self):
		self._session.commit()

	def train(self, sentence, label):
		self._validate_sentence(sentence)
		punc = tuple([word for word, pos in sentence.remainder])
		if len(punc) == 0:
			return
		scores, probs = [], []
		for phrase in sentence.phrases:
			_label, score, estimate = self.classifier.get_prediction(phrase)
			scores.append(score)
			probs.append(estimate)
		if len(scores) == 0:
			return
		f = Feature(punc, scores, probs, label)
		self._session.add(f)

	def _match(self, punc):
		for obj in self._session.query(Feature).filter_by(nonphrase_vector=punc):
			yield obj

	@classmethod
	def _fft_signal(cls, signal, length=None):
		if length is None:
			length = len(signal)
			if length % 2 != 0:
				length += 1

		signal = cls.to_complex(signal)

		if len(signal) % 2 != 0:
			signal = cls.pad_end(signal, 1)

		padding = (abs(len(signal) - length))/2
		if padding > 0:
			signal = cls.pad_sim(signal, padding)

		if not len(signal) == length:
			raise ValueError(("Need to be the same length: ", len(signal), length))

		power_pad = cls.next_pow2(len(signal))
		pad_toadd = power_pad - len(signal)

		signal = cls.pad_end(signal, pad_toadd)

		return signal

	def get_prediction(self, sentence, phrase_trace=[]):
		punc = tuple([word for word, pos in sentence.remainder])
		scores, probs = [], []
		total_pos, total_neg = 0, 0
		for phrase in sentence.phrases:
			label, score, estimate = self.classifier.get_prediction(phrase)
			scores.append(score)
			probs.append(estimate)
			
			if type(phrase_trace) == types.ListType:
				phrase_trace.append((phrase, estimate, score, label))
			else:
				phrase_trace[phrase] = (estimate, score, label)

			if label == 1:
				total_pos += 1
			else:
				total_neg += 1

		if len(scores) == 0:
			return 0, 0, 0, 0, 0, [], [] 

		c_scores = self._fft_signal(scores)
		c_scores = fft(c_scores)

		best_correlation, best_label, best_probability = 0, 0, [0]
		pos, neg = 0, 0
		for f in self._match(punc):
			# Convert to complex
			m_scores = fft(self._fft_signal(f.phrase_scores))

			if len(m_scores) != len(c_scores):
				continue

			cnv = [i * j.conjugate() for i, j in zip(scores, m_scores)]
			res = ifft(cnv)
			correlation_signal = [r.real for r in res]
			corr = max(correlation_signal)
			if corr > best_correlation:
				best_correlation = corr 
				best_label = f.label 
				best_probability = f.phrase_probs
				if best_label == 1: 
					pos += 1
				elif best_label == -1:
					neg += 1

		# Work out the average probability of the first
		average_prob = sum(probs)/len(probs) + best_correlation*sum(best_probability)/len(best_probability)
		average_prob/= 1 + best_correlation
		corr_mult = 1
		if best_label == -1:
			corr_mult = -1

		if average_prob <= 0.5:
			best_label = 0

		return best_label, corr_mult*best_label, average_prob, total_pos, total_neg, probs, scores



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
	def pad_end(cls, arr, amount):
		return arr + [0 for i in range(amount)]

	@classmethod
	def next_pow2(cls, of):
		cur = 1
		while cur < of:
			cur *= 2

		return cur 