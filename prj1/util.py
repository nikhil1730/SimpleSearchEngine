'''
   utility functions for processing terms
    shared by both indexing and query processing
'''
import nltk
from nltk.stem.porter import *
import re
import norvig_spell
from norvig_spell import *


def tokenizer(text):
    text = re.sub("[^a-zA-Z]+", " ", text)
    tokens = nltk.tokenize.word_tokenize(text)
    return tokens

# ''' indexing a docuemnt, using the simple SPIMI algorithm, but no need to store blocks due to the small collection we are handling. Using save/load the whole index instead'''
# 1. Convert to lower cases,
# 2. Remove stopwords,
# 3. Stemming
def preprocessing_txt(text, query):
    tokens = text.split()
    # tokens = tokenizer(text)
    stemmer = PorterStemmer()
    processedText = ""
    removedStopwords = []
    stemmedWords = []
    if query == 'true':
        for i in range(len(tokens)):
            tokens[i] = correction(tokens[i])
    for token in tokens:
        token = token.lower()
        if token not in open('stopwords').read():
            processedText += stemmer.stem(token)
            processedText += " "
            if query == 'test':
                stemmedWords.append(stemmer.stem(token))
        elif query == 'test':
            removedStopwords.append(token)
    if query == 'test':
        print('Removed stop words are:' + str(removedStopwords))
        print('Stemmed words are:     ' + str(stemmedWords))
    return processedText

def isStopWord(word):
    n = 0
    for i in word.split():
        if i not in open('stopwords').read():
            n += 1
            if n == len(word.split()) - 1:
                print('No stop words founds')

def stemming(word):
    ''' return the stem, using a NLTK stemmer. check the project description for installing and using it'''

    # ToDo


