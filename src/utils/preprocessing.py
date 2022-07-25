import re
import string
import preprocessor as p   # this is the tweet-preprocessor library
import emoji
import random
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

random.seed(10)

custom_stopwords = ['n', '\n', 'http', 'www', 'page']

class Preprocessor:
    def __init__(self):
        pass
        self.lemmatizer = WordNetLemmatizer()
    
    def _punctuation(self, val):
        """
        Punctuation Removal

        :param val: value to handle
        """
        val = re.sub(r'[^\w\s]', ' ', val)
        val = re.sub('_', ' ', val)
        val = val.translate(str.maketrans('', '', string.punctuation))
        return val

    def _whitespace(self, val):
        """
        Whitespace Removal

        :param val: value to handle
        """
        return " ".join(val.split())

    def _numbers(self, val):
        """
        Numbers Removal

        :param val: value to handle
        """
        val = re.sub('[0-9]+', '', val)
        return val

    def _unicode(self, val):
        """
        Handle Unicode

        :param val: value to handle
        """
        val = unidecode(val).encode("ascii")
        val = str(val, "ascii")
        return val

    def _stopwords(self, val):
        """
        Remove stopwords

        :param val: value to handle
        """
        tokens = word_tokenize(val)
        stop = stopwords.words('english') + custom_stopwords
        filtered = [
            word for word in tokens if word not in stop]
        return ' '.join(filtered)

    def _lemmatize(self, val):
        """
        Lemmatize

        :param val: value to handle
        """
        tokens = word_tokenize(val)
        lemmatized = [self.lemmatizer.lemmatize(word) for word in tokens]
        return ' '.join(lemmatized)

    def _vocabularize(self, val):
        """
        Remove repeated words

        :param val: value to handle
        """
        tokens = word_tokenize(val)
        vocab=[]

        for token in tokens:
            if not token in vocab:
                vocab.append(token)
        return ' '.join(vocab)

    def clean(self, document):        
        document = document.lower()
        document = ' '.join(self._punctuation(emoji.demojize(document)).split())
        document = p.clean(document)
        document = self._numbers(document)
        document = self._unicode(document)
        document = self._whitespace(document)
        document = self._lemmatize(document)
        document = self._stopwords(document)
        document = self._vocabularize(document)
        
        return document