import cPickle

from sklearn import tree
from nltk.tokenize import sent_tokenize

from taggers import TopiaTagger
from sentences_meta import MetaSentenceClassifier
from models import Sentence

def mean(of):
    if len(of) == 0:
        return 0
    return sum(of)/len(of)

def variance(of):
    if len(of) == 0:
        return 0
    m = mean(of)
    return sum([(i-m)*(i-m) for i in of])/len(of)

class DocumentClassifier(object):

    def __init__(self, classification_file='clf.pickle'):
        fp = open(classification_file, 'r')
        self.tree = cPickle.load(fp)
        self.clas = MetaSentenceClassifier("sqlite:///sentences.db")
        self.tag  = TopiaTagger()

    def classify(self, document_text, sentence_trace=[]):
        # Break the text into sentences 
        raw_sentences = sent_tokenize(document_text)
        sentences = []
        for sentence in raw_sentences:
            try:
                s = Sentence(sentence, self.tag)
                sentences.append(s)
            except ValueError as ex:
                print sentence, ex 
        # Score those sentences
        scores = []
        for s in sentences:
            subtrace = []
            score = self.clas.get_prediction(s, subtrace)
            scores.append(score)
            sentence_trace.append((s, score, subtrace))
        #
        # Compute statistics
        #
        pos_phrases, neg_phrases = 0, 0
        pos_sentences, neg_sentences = 0, 0
        phrase_probs, phrase_scores = {-1: [], 0: [], 1:[]}, {-1: [], 0: [], 1:[]}
        total_classified = 0
        probabilities = {-1: [], 0: [], 1:[]}
        for position, (label, average, prob, pos, neg, probs, _scores) in enumerate(scores):

            # Positive, negative, classified statistics 
            if label != 0:
                total_classified += 1
                if label == 1:
                    pos_sentences += 1
                if label == -1:
                    neg_sentences += 1
            pos_phrases += pos; neg_phrases += neg
            for p in probs:
                phrase_probs[label].append(p)
            for s in _scores:
                phrase_scores[label].append(s)
            probabilities[label].append(prob)

        # Generate feature vector
        row = [position, total_classified, pos_sentences, neg_sentences, pos_phrases, neg_phrases]

        for stat in [phrase_probs, phrase_scores, probabilities]:
            for func in [mean, variance]:
                for label in [-1, 0, 1]:
                    row.append(func(stat[label]))

        # Classify 
        labels = self.tree.predict([row])
        for label in labels:
            return [label] + row