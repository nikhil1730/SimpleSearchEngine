'''

Index structure:

    The Index class contains a list of IndexItems, stored in a dictionary type for easier access

    each IndexItem contains the term and a set of PostingItems

    each PostingItem contains a document ID and a list of positions that the term occurs

'''
import util
import doc
import json
import sys
import math
import time
from cran import *
from util import *

class Posting:
    def __init__(self, docID):
        self.docID = docID
        self.positions = []

    def append(self, pos):
        self.positions.append(pos)

    def sort(self):
        ''' sort positions'''
        self.positions.sort()

    def merge(self, positions):
        self.positions.extend(positions)

class IndexItem:
    def __init__(self, term):
        self.term = term
        self.posting = {} #postings are stored in a python dict for easier index building
        self.sorted_postings= [] # may sort them by docID for easier query processing

    def add(self, docid, pos):
        ''' add a posting'''
        if not docid in self.posting:
            self.posting[docid] = Posting(docid)
            self.posting[docid] = pos

class InvertedIndex:
    inverted_index = {}
    inverted_index_temp = {}
    def __init__(self):
        self.items = {} # list of IndexItems
        self.nDocs = 0  # the number of indexed documents
  
    def indexDoc(self, doc): # indexing a Document object using functions in util.py
        processedText = preprocessing_txt(doc.body,'')
        for word in processedText.split():
            position = wordPositions(word, processedText)
            if word in self.items.keys(): 
                if not int(doc.docID) in list(self.items[word].posting.keys()):
                    self.items[word].add(int(doc.docID), position)
            else:
                index_item = IndexItem(word)
                index_item.add(int(doc.docID), position)
                self.items[word] = index_item
        for i in self.items:
            dictionary = {}
            x = 0
            for j in self.items[i].posting:
                listposition = []
                for k in self.items[i].posting[j]:
                    listposition.append(k)
                dictionary[j] = listposition
            self.inverted_index_temp[i] = dictionary
        self.inverted_index = self.inverted_index_temp    

    def find(self, term):
        return self.items[term]

    # Calculating and saving to disk TFIDF for the documents in the cran.all and creating, serialize/deserialize the index indexing for the terms from all docs with their positions
    def save(self, savefile, termFrequency, totalDocs, test):
        for i in termFrequency:
            termFrequency[i] = calculateIDF(termFrequency[i], self.inverted_index, totalDocs)
        # Storing tfidf scores for calculating Cosine similarity
        if test == 'true':
            with open('test_tfidf','w') as data:
                json.dump(termFrequency, data)
            with open('test_index','w') as fp:
                json.dump(self.inverted_index, fp)

        else:
            with open('tfidf','w') as data:
                json.dump(termFrequency, data)
            with open(savefile,'w') as fp:
                json.dump(self.inverted_index, fp)

# Testing the code on
# 1. Index Data Saving and Loading on sample data
# 2. Checking if StopWords are removed and Stemming is done properly
# 3. Checking for TF IDF scores whether they are properly calculated.
# TF(t) = (Number of times term t appears in a document) / (Total number of terms in the document)
# IDF(t) = 1 + log_10(Total number of documents / Number of documents with term t in it).
# TF-IDF = TF * IDF
def test():
    print()
    print('========= Working on Test Cases =========')
    testDict = {}
    manual_indexing = {"game": {"1": [1, 3]}, "life": {"1": [2], "2": [2]}, "everlast": {"1": [4]}, "learn": {"1": [5], "3": [3]}, "unexamin": {"2": [1]}, "worth": {"2": [3]}, "live": {"2": [4]}, "never": {"3": [1]}, "stop": {"3": [2]}}
    manual_tfidf = {"1": {"game": 0.590848501887865, "life": 0.2352182518111363, "everlast": 0.2954242509439325, "learn": 0.2352182518111363}, "2": {"unexamin": 0.3692803136799156, "life": 0.29402281476392034, "worth": 0.3692803136799156, "live": 0.3692803136799156}, "3": {"never": 0.4923737515732208, "stop": 0.4923737515732208, "learn": 0.3920304196852271}}
    indexingCranfield('test.txt', 'test_index', 'true')
    test_data = 'This method is to do an experimental with the experiment data for tokenization,stemming and Stopwords '
    print ('Data before processing    ' + test_data)
    processed_testData = preprocessing_txt(test_data, 'test')
    print ('Data after processing     ' + processed_testData)
  
    with open('test_index') as openTestFile:
            test_indexing = json.load(openTestFile)
    with open('test_tfidf') as testtfidfFile:
            test_tfidfScore = json.load(testtfidfFile)
    if manual_indexing == test_indexing:
        print('Indexing Saving, Loading, calculations are according to the manual results.')
        print('Manual Result  ' + str(manual_indexing))
        print('Test Result    ' + str(test_indexing))
    else:
        print('Indexing Saving, Loading, calculations are not according to the manual results.')
    if manual_tfidf == test_tfidfScore:
        print('TF-IDF values are calculated correctly')
        print('Manual Result  ' + str(manual_tfidf))
        print('Test Result    ' + str(test_tfidfScore))
    else:
        print('TF-IDF values are not calculated correctly')
        
# Indexing the Cranfield dataset and save the index to a file
# The index is saved to index_file and TFIDF scores are stored in tfidf scores for the terms in the documents from cran.all
def indexingCranfield(cranfile,savefile, test):
    # command line usage: "python index.py cran.all index_file"
    file = CranFile(cranfile)
    invertedIndex = InvertedIndex()
    temp = {}
    termFrequency = {}
    n = 0
    totalDocs = len(file.docs)
    print(str(len(file.docs)) + ' documents are present in the dataset.')
    for i in file.docs:
        if n == totalDocs: break
        else: 
            # For calculating the Term frequency according to the documents 
            temp = calculateTF(preprocessing_txt(i.body,''))
            termFrequency[i.docID] = temp
            # For creating the index_file
            invertedIndex.indexDoc(i)
            n += 1    
    invertedIndex.save(savefile, termFrequency, totalDocs, test)
    print ('Indexing file creation  is done')

# The below method calculates TF IDF scores considering the termfrequency list generated from the indexing list 
def calculateIDF(doc, indexData, totalDocs):
    for i in doc.keys():
        if i in indexData.keys():
            count = len(indexData[i].keys())
            doc[i] = doc[i] * float( 1 + math.log10(totalDocs/count))
    return doc

# For calculating the normalized Term Frequency of the terms in the query
def calculateTF(text):
    textList = text.split()
    count = 0
    textTF = {}
    for i in range(len(textList)):
        if textList[i] in textTF.keys():
            textTF[textList[i]] += float(1/len(textList))
        else:
            textTF[textList[i]] = float(1/len(textList))
    return textTF

# To find the normalized term location in the processed query
def wordPositions(word, processedText):
    pos = 1
    positions = []
    for data in processedText.split():
        if word == data:
            positions.append(pos)
        pos += 1
    return positions

if __name__ == '__main__':
    indexingCranfield(str(sys.argv[1]),str(sys.argv[2]), '')
    test()
