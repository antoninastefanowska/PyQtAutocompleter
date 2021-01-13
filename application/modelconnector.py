from gensim.models import FastText
import spacy
import tensorflow as tf

import numpy as np

class ModelConnector:
    SEQUENCE_SIZE = 5
    TOKENIZER_DATA_PATH = r'./resources/models/en_core_web_sm'
    VECTORS_DATA_PATH = r'./resources/models/vectors.bin'
    MODEL_DATA_PATH = r'./resources/models/model'

    def __init__(self):
        self.count = 0
        self.last_vectorized_sequence = None
        self.last_tokens = None
        self.tokenizer = None
        self.vectors = None
        self.model = None
        self.currently_learning = False

    def load_models(self):
        self.tokenizer = spacy.load(ModelConnector.TOKENIZER_DATA_PATH, disable = ['tagger', 'parser', 'ner'])
        print('Tokenizer loaded.')
        self.vectors = FastText.load(ModelConnector.VECTORS_DATA_PATH)
        print('Vectorizer loaded.')
        self.model = tf.keras.models.load_model(ModelConnector.MODEL_DATA_PATH)
        print('Neural network model loaded.')

    def tokenize(self, text):
        doc = self.tokenizer(text)
        tokens = [token.lemma_.lower().strip() if token.lemma_ != '-PRON-' else token.lower_ for token in doc if token.is_alpha and token.is_ascii and not token.is_stop and (token.lemma_.isalpha() or token.lemma_ == '-PRON-')]
        return tokens

    def vectorize(self, tokens, token_index):
        sequence_vectors = []
        for i in range(token_index - ModelConnector.SEQUENCE_SIZE, token_index):
            if i < 0:
                sequence_vectors.append(np.zeros(100, dtype='float32'))
            else:
                try:
                    sequence_vectors.append(self.vectors.wv[tokens[i]])
                except KeyError:
                    sequence_vectors.append(np.zeros(100, dtype='float32'))
        return np.array([np.array(sequence_vectors)])

    def classify(self, input_vectors):
        output = self.model.predict(input_vectors)[0]
        return output

    def select(self, output, last_token):
        indexes = np.argpartition(output, -5)[-5:]
        words = [self.vectors.wv.index2word[index] for index in indexes]
        while last_token in words:
            index = self.vectors.wv.vocab[last_token].index
            output[index] = 0
            indexes = np.argpartition(output, -5)[-5:]
            words = [self.vectors.wv.index2word[index] for index in indexes]
        return words

    def predict_words(self, tokens):
        self.last_vectorized_sequence = self.vectorize(tokens, len(tokens))
        output = self.classify(self.last_vectorized_sequence)
        words = self.select(output, tokens[-1])
        return words

    def learn(self, last_token):
        if last_token in self.vectors.wv.vocab and not self.currently_learning:
            self.currently_learning = True
            label = np.array([self.vectors.wv.vocab[last_token].index])
            self.model.fit(self.last_vectorized_sequence, label, batch_size=1)
            self.currently_learning = False
            print('Weights updated.')

    def save_model(self):
        self.model.save(ModelConnector.MODEL_DATA_PATH)
        print('Model saved.')