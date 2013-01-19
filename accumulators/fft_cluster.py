import sys

from scipy.fftpack import ifft, fft
from classifier import SentenceClassifer
from fft import correlate

class ClusteringFFTClassifier(SentenceClassifer):

	def __init__(self, feature_db, threshold = 0.9):
		self._feature_db = feature_db
		self._signals = []
		self._signal_length = 0
		self._threshold = threshold

	@classmethod
	def _build_score_vector(cls, sentence):
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

	def _yield_naive_correlations(self, signal):
		for _id, (_signal, _label) in enumerate(self._signals):
			correlation_signal = correlate(signal, _signal)
			correlation = max(correlation_signal)
			yield (_id, _label, correlation)

	def train(self, tagger, scorer, rescorer, print_summary=True):

		source_counter, reject_counter, length_reject_counter = 0, 0, 0
		consolidation_counter = 0

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

			add_to_self = True
			signals_rem = []
			# Decide how well this sentence fares with existing sentences
			for _id, _label, correlation in self._yield_naive_correlations(signal):
				# If the sentence correlates well,
				if correlation > self.threshold:
					# If the label is the same as the well correlated one, then this sentence
					# can't tell us anything new
					if _label == label:
						add_to_self = False 
						break 
					# Otherwise, this is evidence of a sentence structure which has no
					# intrinsic sentiment, we should remove those sentences it correlates well with
					signals_rem.append(_id)
					label = 0

			# If we have some signals to remove...
			if len(signals_rem) > 0:
				new_signals = []
				for _id, _signal in enumerate(self._signals):
					if _id not in signals_rem:
						new_signals.append(_signal)
					else:
						consolidation_counter += 1
				self._signals = new_signals

			# Finally, if we've decided to add this sentence 
			if add_to_self:
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


	def classify_sentence(self, sentence, print_summary = True):
		# Work out the signal vector
		signal = self._build_score_vector(sentence)

		# See how well it correlates to our existing signals 
		best_correlation, best_label = 0, 0
		for _signal, _label in self._signals:
			correlation_signal = correlate(signal, _signal)
			correlation = max(correlation_signal)
			if correlation > best_correlation:
				best_correlation = correlation
				best_label = _label 

		return best_label, best_correlation, None
