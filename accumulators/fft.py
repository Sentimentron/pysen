#!/usr/bin/python
import random
import sys
import types 
from numpy import complex64
from scipy.fftpack import ifft, fft
from classifier import SentenceClassifier

class SentenceFFTClassifier(SentenceClassifier):

	def __init__(self, feature_db):
		self.feature_db = feature_db
		self.signals = []
		self._signal_length = 0

	def _fft_signal(self, signal):
		signal = to_complex(signal)

		if len(signal) % 2 != 0:
			signal = pad_end(signal, 1)

		padding = (abs(len(signal) - self._signal_length))/2
		if padding > 0:
			signal = pad_sim(signal, padding)

		if not len(signal) == self._signal_length:
			raise ValueError(("Need to be the same length: ", len(signal), self._signal_length))

		power_pad = next_pow2(len(signal))
		pad_toadd = power_pad - len(signal)

		signal = pad_end(signal, pad_toadd)

		signal = fft(signal)
		return signal 

	def train(self, tagger, scorer, rescorer):
		self.signals = []
		tmp_signals  = []
		raw_signals  = []
		# Append a score vector to this-self
		for text, label, extra in self.feature_db.get_all_features():
			tagged = tagger.tag(text)
			scored = scorer.score(tagged)
			scored = list(rescorer.rescore(scored))

			signal = []
			for word, pos, norm, score in scored:
				overall, count = 0, 0
				if score is None:
					signal.append(0.0)
					continue
				signal.append(score['pos'] - score['neg'])

			self._signal_length = max(self._signal_length, len(signal))
			tmp_signals.append((signal, label))

		if self._signal_length %2 != 0:
			self._signal_length += 1

		# Run the FFT on each signal
		for signal, label in tmp_signals:
			signal = self._fft_signal(signal)
			self.signals.append((signal, label))


	def classify_sentence(self, sentence):
		signal = []
		if len(sentence) > self._signal_length:
			return 0, 0, None
		for word, pos, norm, score in sentence:
			if score is None:
				signal.append(0.0)
			else:
				if type(score) is types.DictType:
					signal.append(score['pos'] - score['neg'])
				else:
					signal.append(score)

		best_correlation, best_label = 0, 0
		# Compute the FFT of the score vector
		signal = self._fft_signal(signal)

		#comp = random.sample(self.signals, 500)
		comp = self.signals
		print >> sys.stderr, "fft: len(comp) is", len(comp)

		for counter, (_signal, _label) in enumerate(comp):
			cnv = [i * j.conjugate() for i, j in zip(signal, _signal)]
			res = ifft(cnv)
			correlation_signal = [r.real for r in res]
			corr = max(correlation_signal)
			if corr > best_correlation:
				best_correlation = corr 
				best_label = _label 

		return best_label, best_correlation, None 


def to_complex(arr):
	return [complex64(a) for a in arr]

def ccmult(i, j):
	return i * j.conjugate()

def pad_sim(arr, amount):
	ret = [0 for i in range(amount)]
	ret += arr 
	ret += [0 for i in range(amount)]
	return ret

def next_pow2(of):
	cur = 1
	while cur < of:
		cur *= 2

	return cur 

def pad_end(arr, amount):
	return arr + [0 for i in range(amount)]

def correlate_skip_fft(sig1, sig2):
	cnv = [ccmult(i, j) for i,j in zip(sig1_fft, sig2_fft)]
	res = fft(cnv, power_pad, -1)

def correlate_skip_ff1_onfirst(sig1_fft, sig2):

	sig2 = to_complex(sig2)

	if len(sig2) % 2 != 0:
		sig2 = pad_end(sig2, 1)

	padding = (abs(len(sig1_fft) - len(sig2)))/2
	sig2 = pad_sim(sig2, padding)

	power_pad = next_pow2(len(sig2))
	pad_toadd = power_pad - len(sig2)

	sig2 = pad_end(sig2, pad_toadd)

	sig2_fft = fft(sig2)
	cnv = [i * j.conjugate() for i,j in zip(sig1_fft, sig2_fft)]
	res = ifft(cnv)
	return res

def correlate(sig1, sig2):

	sig1 = to_complex(sig1)
	sig2 = to_complex(sig2)

	if len(sig1) % 2 != 0:
		sig1 = pad_end(sig1, 1)
	if len(sig2) % 2 != 0:
		sig2 = pad_end(sig2, 1)

	#print len(sig1), len(sig2), abs(len(sig1) - len(sig2)),
	padding = (abs(len(sig1) - len(sig2)))/2
	#print padding
	if len(sig1) < len(sig2):
		sig1 = pad_sim(sig1, padding)
	elif len(sig2) < len(sig1):
		sig2 = pad_sim(sig2, padding)

	if not len(sig1) == len(sig2):
		print len(sig1), len(sig2)
		raise ValueError()

	power_pad = next_pow2(len(sig1))
	pad_toadd = power_pad - len(sig1)

	sig1 = pad_end(sig1, pad_toadd)
	sig2 = pad_end(sig2, pad_toadd)

	sig1_fft = fft(sig1)
	sig2_fft = fft(sig2)

#	print sig1_fft, sig2_fft

	cnv = [i * j.conjugate() for i,j in zip(sig1_fft, sig2_fft)]
	res = ifft(cnv)

	return [r.real for r in res]