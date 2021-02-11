
'''
query processing

'''
import util
import json
import time
import random
import math
import sys
from util import *
from cran import *
from cranqry import *


# Testing the test case like converting queries to terms, checking tfidf scores and cosine similarities.
def test():
    ''' test your code thoroughly. put the testing cases here'''
    manual_boolean = ['1']
    manual_vector = [1, 3, 2]
    manula_cosine = [1.0, 0.7071067811865476, 0.7071067811865475]
    print('==== Working on Test cases ====')


    for i in range(len(test_sampleQueries)):
        booleanQuery(test_data, test_sampleQueries[i], 'test')
        vectorQuery(test_data, test_sampleQueries[i], test_tfidf,'',3)
    print ('Pass')    

# For vectorQuery, the program will output the top 3 most similar documents for a query using the cosine similarity
# Returns top k pairs of (docID, similarity), ranked by their cosine similarity with the query in the descending order
def vectorQuery(self, query, tfidf, eval, totalDocs):
    queryTerms = preprocessing_txt(query, 'true')
    if eval == 'test':
        print('For making sure queries in Vector Modelare converted to terms and the length of the termslist is' + str(len(queryTerms.split())))
    tffidfQuery, tffidfIndex, tfidfDocs, docTF = {}, {}, {}, {}
    # totalDocs = 1400
    docSimilarity = []
    tffidfQuery = tffIdfQuery(queryTerms.split(), self, totalDocs)
    tfidfIndex = tfIdfIndex(queryTerms.split(), self, tfidf, totalDocs)
    for doc in range(totalDocs):
        for i in queryTerms.split():
            tfidfDocs[i] = {}
            tfidfDocs[i] = tfidfIndex[i][str(doc+1)]
        temp = cosineSimilarity(tffidfQuery, tfidfDocs)
        docTF[temp] = {}
        docTF[temp] = str(doc + 1)
        docSimilarity.append(temp)
    docSimilarity = sorted(docSimilarity, key = lambda x:float(x))
    
    if eval == 'vector':
        ndcgVector = [0,0,0,0,0]
        cosine_value = [0,0,0,0,0]
        for i in range(5):
                if i < len(docSimilarity):
                    ndcgVector[i] = docTF[docSimilarity[totalDocs-(i+1)]]
                    cosine_value[i] = docSimilarity[totalDocs-(i+1)]
                else:
                    ndcgVector[i] = 0
                    cosine_value[i] = 0.0
        return ndcgVector+cosine_value
    elif eval == 'time':
        return
    else:
        print('Vector Model -- Top 3 ranked Documents are ' + docTF[docSimilarity[totalDocs-1]] +', ' +
         docTF[docSimilarity[totalDocs-2]] +', ' + docTF[docSimilarity[totalDocs-3]])
        print('                Their scores are           ' + str(docSimilarity[totalDocs-1]) +', ' + str(docSimilarity[totalDocs-2]) +', ' + str(docSimilarity[totalDocs-3]))

# Calculating cosine similarity for ranking the documents against documents
def cosineSimilarity(querytfidf, doctfidf):
    modQuery = 0
    modDoc = 0
    dotProduct = 0
    for i in querytfidf.keys():
        modQuery += (querytfidf[i] * querytfidf[i])
        modDoc += (doctfidf[i] * doctfidf[i])
        dotProduct += (querytfidf[i] * doctfidf[i])
    if modQuery*modDoc == 0 :
        modDoc = 0.00000000000001
        modQuery = 0.0000000000001
    return float(dotProduct/(math.sqrt(modQuery) * math.sqrt(modDoc)))

# To calculate TDIDF scores for the query sample.
def tffIdfQuery(queryList, self, totalDocs):
    queryDict = {}
    for term in queryList:
        if term in queryDict.keys():
            if term in self:
                queryDict[term] += ((1/len(queryList)) * (1 + math.log10(totalDocs/len(self[term].keys()))))
            else:
                queryDict[term] += ((1/len(queryList)) * (1 + math.log10(1)))
        else:
            queryDict[term] = {}
            if term in self:
                queryDict[term] = ((1/len(queryList)) * (1 + math.log10(totalDocs/len(self[term].keys()))))
            else:
                queryDict[term] = ((1/len(queryList)) * (1 + math.log10(1)))
    return queryDict  

# Fetching the documents with the TFIDF scores stored in tfidf file for every token in the query sample
def tfIdfIndex(queryList, self, tf, totalDocs):
    dict = {}
    for i in queryList:
        dict[i] = {}
        if i in self:
            # print(str(self[i].keys()))
            for k in range(totalDocs):
                if str(k+1) in self[i].keys():
                   dict[i][str(k+1)] = 0
                   dict[i][str(k+1)] = tf[str(k+1)][i] 
                else:
                   dict[i][str(k+1)] = 0 
            # for j in self[i].keys():
            #     dict[i] = {}
            #     dict[i][j] = 0
            #     dict[i][j] = tf[j][i]
        else:
            for m in range(totalDocs):
                dict[i][str(m+1)] = 0
    return dict

# Boolean query processing; note that a query like "A B C" is transformed to "A AND B AND C" for retrieving posting lists and merge them.
# Return a list of docIDs which matches with the query i.e. relavant documents from cran.all
def booleanQuery(self, query, eval):
        processedText = preprocessing_txt(query, 'true')
        if eval == 'test':
            print('For making sure queries are converted to terms and the length of the termslist is    ' + str(len(processedText.split())))
        queryDocs = []
        temp = []
        ndcgBoolean = []
        n = 0
        for i in processedText.split():
            if i in self:
                queryDocs.append(list(self[i].keys()))
        for i in range(len(queryDocs)):
            if i == 0:
                temp = queryDocs[i]
            else:
                temp = commonDocs(queryDocs[i],  temp)
        if eval == 'boolean':
            if len(temp) == 0:
                noDocs = [0,0,0,0,0]
                return noDocs
            else:
                for i in range(5):
                    if i < len(temp):
                        ndcgBoolean.append(temp[i])
                    else:
                        ndcgBoolean.append(0)
                return ndcgBoolean
            print(ndcgBoolean)
        elif eval == 'time':
            return
        elif eval == 'test':
            if len(temp) > 0:
                print("The actual document which contains the query are --" + str(temp)[1:-1])   
        else:
            if len(temp) == 0:
                print('No Matching Results found')
            else:
                print("Boolean Model -- " + str(len(temp)) + " documents which contains the query are " + str(temp)[1:-1])
            return

# To find the common documents between two documents while calculating results for boolean model
def commonDocs(a, b):
    docs=[]
    for i in range(len(a)):
        for j in range(len(b)):
            if a[i] == b[j]:
                docs.append(a[i])
                break
    return docs 

if __name__ == '__main__':
    file = loadCranQry(sys.argv[3])
    n = 0
    data = {}
    mode = int(sys.argv[2])
    
    test_sampleQueries = []
    test_sampleQueries = ['life and learning']
    if mode == 2:
        queryDocs = []
        sampleQueries = []
        queryIds = list(file.keys())
        totalSamples = int(sys.argv[4])
        querySamples = random.choices(queryIds, k=totalSamples)
        querySamples = list(set(querySamples))
        for i in querySamples:
            sampleQueries.append(file[i].text)
        print(querySamples)
    else:
        queryId = str(sys.argv[4])
        if len(queryId) == 2:
            queryId = '0' + queryId
        query = file[queryId].text
        print(queryId + "    " + query)
    with open(sys.argv[1]) as fp:
            data = json.load(fp)
    with open('tfidf') as tfidfFile:
            tfidf = json.load(tfidfFile)
    with open('test_index') as fp:
            test_data = json.load(fp)
    with open('test_tfidf') as tfidfFile:
            test_tfidf = json.load(tfidfFile)
    
    if mode == 0:
        booleanQuery(data, query, '')
    elif mode == 1:
        vectorQuery(data, query, tfidf,'', 1400)
    else:
        startBool = time.process_time()
        for i in sampleQueries:
            booleanQuery(data, i, 'time')    
        print('Boolean Time         ' + str(time.process_time() - startBool))
        startVector = time.process_time()
        for i in sampleQueries:
           vectorQuery(data, i, tfidf, 'time',1400)    
        print('Vector Time          ' + str(time.process_time() - startVector))

    test()