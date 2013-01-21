import itertools
import multiprocessing
import sys
import types

from scipy.fftpack import ifft, fft
from classifier import SentenceClassifier
from fft import correlate

def _compute_naive_correlation(stored_signal):
	signal, (_id, (_signal, _label)) = stored_signal
	correlation_signal = correlate(signal, _signal)
	correlation = max(correlation_signal)
	return (_id, _label, correlation)

class ClusteringFFTClassifier(SentenceClassifier):

	def __init__(self, feature_db, threshold = 0.5):
		self._feature_db = feature_db
		self._signals = []
		self._signal_length = 0
		self._threshold = threshold

	@classmethod
	def _build_score_vector(cls, sentence):
		signal = []
		for word, pos, norm, score in sentence:
			if score is None:
				signal.append(0.0)
			else:
				if type(score) is types.DictType:
					signal.append(score['pos'] - score['neg'])
				else:
					signal.append(score)
		return signal

	def _yield_naive_correlations(self, signal):
		for _id, (_signal, _label) in enumerate(self._signals):
			correlation_signal = correlate(signal, _signal)
			correlation = max(correlation_signal)
			yield (_id, _label, correlation)

	def train(self, tagger, scorer, rescorer, print_summary=True):

		source_counter, reject_counter, length_reject_counter = 0, 0, 0
		consolidation_counter = 0

		p = multiprocessing.Pool()

		for text, label, extra in self._feature_db.get_all_features():
			# Tag and score the sentences using the supplied classifier
			source_counter += 1
			tagged = tagger.tag(text)
			scored = scorer.score(tagged)
			scored = list(rescorer.rescore(scored))
			if len(scored) < 5:
				length_reject_counter += 1
				continue
			signal = self._build_score_vector(scored)
			if signal is None:
				reject_counter += 1
				continue

			add_to_self = True
			signals_rem = []
 			map_src = itertools.izip(itertools.repeat(signal), list(enumerate(self._signals)))

 			if print_summary:
				print >> sys.stderr, "correlating...",
			correlations = p.map(_compute_naive_correlation, map_src)
			if print_summary:
				print >> sys.stderr, "done (%d/%d)" %(len(correlations), source_counter)

			# Decide how well this sentence fares with existing sentences
			for _id, _label, correlation in correlations:
				if print_summary:
					pass
					#print >> sys.stderr, _id, _label, correlation, text
				# If the sentence correlates well,
				if correlation > self._threshold:
					# If the label is the same as the well correlated one, or the correlated one is zero
					# then this sentence can't tell us anything new
					if _label == label:# or _label == 0:
						add_to_self = False 
						break 
					# Otherwise, this is evidence of a sentence structure which has no
					# intrinsic sentiment, we should remove those sentences it correlates well with
					signals_rem.append(_id)
					label = 0

			# If we have some signals to remove...
			if len(signals_rem) > 0:
				#print signals_rem
				new_signals = []
				for _id, _signal in enumerate(self._signals):
					if _id not in signals_rem:
						new_signals.append(_signal)
					else:
						consolidation_counter += 1
				self._signals = new_signals

			# Finally, if we've decided to add this sentence 
			if add_to_self:
				#print signal, label, self._signals
				self._signals.append((signal, label))
			else:
				reject_counter += 1

		# Print a summary
		if print_summary:
			print >> sys.stderr, self, "TRAINING COMPLETE"
			print >> sys.stderr, "Threshold: %.2f" % (self._threshold, )
			print >> sys.stderr, "Signals:", len(self._signals)
			print >> sys.stderr, "Rejections (too short):", length_reject_counter
			print >> sys.stderr, "Rejections (indistinct):", reject_counter
			print >> sys.stderr, "Consolidations:", consolidation_counter
			print >> sys.stderr, "Signals analysed:", source_counter
			print >> sys.stderr, "Signals with no sentiment:", len(filter(lambda x: x[1] == 0, self._signals))

	def classify_sentence(self, sentence, print_summary = True):
		# Work out the signal vector
		signal = self._build_score_vector(sentence)

		# See how well it correlates to our existing signals 
		best_correlation, best_label = 0, 0
		for _signal, _label in self._signals:
			#print _signal, _label
			correlation_signal = correlate(signal, _signal)
			correlation = max(correlation_signal)
			#print correlation
			if correlation > best_correlation:
				best_correlation = correlation
				best_label = _label 
		if print_summary:
			print >> sys.stderr, best_label, best_correlation

		return best_label, best_correlation, None
