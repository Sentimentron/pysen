from scipy.fftpack import ifft, fft


from fft import SentenceFFTClassifier
import math
import types

class Bin(object):

	def __init__(self, _min, _max):
		self.min = _min 
		self.max = _max 
		self.signals = []

	def in_range(self, length):
		return length > self.min and length <= self.max

	def insert(self, signal, label):
		self.signals.append((signal, label))

	def get_max(self):
		return self.max

	def __iter__(self):
		for thing in self.signals:
			yield thing

	def __repr__(self):
		return "Bin(min: %d, max: %d)" % (self.min, self.max)

class SentenceFFTBinClassifier(SentenceFFTClassifier):

	def __init__(self, feature_db, bins=5):
		super(SentenceFFTBinClassifier, self).__init__(feature_db)
		self.bin_count = bins 
		self.bins = []


	def train(self, tagger, scorer, rescorer):
		self.signals = []
		tmp_signals  = []
		raw_signals  = []
		signal_lens  = []
		_max_len, _min_len = 0, 0
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

			tmp_signals.append((signal, label))
			signal_lens.append(len(signal))
		# Get the largest and smallest sentence lengths
		_max_len, _min_len = max(signal_lens), min(signal_lens)

		# Decide the range of each bin 
		delta = _max_len - _min_len
		bin_width = int(math.ceil(1.0 * delta / self.bin_count))

		# Generate bin-stops
		_stops  = [bin_width*i for i in range(self.bin_count+1)]
		_starts = _stops[0:-1]
		_ends   = _stops[1:]

		# Create the bins
		for start, end in zip(_starts, _ends):

			if start % 2 != 0:
				start += 1
			if end % 2 != 0:
				end += 1

			b = Bin(start, end)
			print b
			self.bins.append(b)

		# Append the signals to the bin which fits
		for signal, label in tmp_signals:
			length = len(signal)

			if length == 0:
				continue

			# Find the bin 
			candidate_bins = filter(lambda x: x.in_range(length), self.bins)
			if len(candidate_bins) != 1:
				raise ValueError((self.bins, length))

			candidate_bin  = candidate_bins[0]

			# Pad the signal and take its FFT 
			max_length = candidate_bin.get_max()
			signal = self._fft_signal(signal, max_length)

			# Insert signal into the bin
			candidate_bin.insert(signal, label)

	def classify_sentence(self, sentence):
		signal = []
		# Generate classification vector (TODO: refactor)
		for word, pos, norm, score in sentence:
			if score is None:
				signal.append(0.0)
			else:
				if type(score) is types.DictType:
					signal.append(score['pos'] - score['neg'])
				else:
					signal.append(score)

		best_correlation, best_label = 0, 0
		length = len(signal)

		# Find the best bin 
		candidate_bins = filter(lambda x: x.in_range(length), self.bins)
		# Couldn't find a bin
		if len(candidate_bins) == 0:
			return 0, 0, None
		assert len(candidate_bins) == 1
		candidate_bin  = candidate_bins[0]

		# Find the correlation of every training signal 
		# within that bin
		for _signal, _label in candidate_bin:
			cnv = [i * j.conjugate() for i, j in zip(signal, _signal)]
			res = ifft(cnv)
			correlation_signal = [r.real for r in res]
			corr = max(correlation_signal)
			if corr > best_correlation:
				best_correlation = corr 
				best_label = _label 

		return best_label, best_correlation, None