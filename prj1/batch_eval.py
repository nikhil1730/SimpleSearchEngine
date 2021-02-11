'''
a program for evaluating the quality of search algorithms using the vector model

it runs over all queries in query.text and get the top 10 results,
and then qrels.text is used to compute the NDCG metric

usage:
    python batch_eval.py index_file query.text qrels.text n

    output is the average NDCG over all the queries for boolean model and vector model respectively.
	also compute the p-value of the two ranking results. 
'''
import metrics
from cranqry import *
import random
import json
from query import *
from metrics import *
from scipy import stats

# Evaluating the NDCG scores for Boolean model and Vector model results against actual data to check the success rate.
# Prints average NDCG scores for the boolean model, Vector model  and p_value score for sample of queries of size k
def eval():
    queryMatchesB = [] 
    queryMatchesV = [] 
    ndcg_scoreB = []
    ndcg_scoreV = []
    for i in range(len(sampleQueries)):
        queryMatchesB = booleanQuery(data, sampleQueries[i], 'boolean')
        ndcg_scoreB.append(calculate_ndgc5(queryMatchesB, mappingDict[querySamples[i]],'boolean'))

        queryMatchesV = vectorQuery(data, sampleQueries[i], tfidf, 'vector', 1400)
        ndcg_scoreV.append(calculate_ndgc5(queryMatchesV, mappingDict[querySamples[i]],'vector'))
    avgBoolean = sum(ndcg_scoreB) / len(ndcg_scoreB)
    avgVector = sum(ndcg_scoreV) / len(ndcg_scoreV)
    p_value = stats.wilcoxon(ndcg_scoreB,ndcg_scoreV)
    print('Average NDCG score for Boolean Model is  ' + str(avgBoolean))
    print('Average NDCG score for Vector Model is   ' + str(avgVector))
    print('P-Value calculated for Boolean Vector is ' + str(p_value))

# Calculating NDCG scores for first 5 results for boolean and vector model.
def calculate_ndgc5(docId,resultedDocs, method):
    y_truth = [0,0,0,0,0]
    y_score = [0,0,0,0,0]
    for i in range(5):
        if docId[i] == 0:
            y_truth[i] = 0
            y_score[i] = 0
        else:
            if method == 'boolean':
                y_score[i] = 1 
            else:
                y_score[i] = docId[5+i] 
            if docId[i] in resultedDocs:
                y_truth[i] = 1
            else:
                y_truth[i] = 0
    ndcgValue = ndcg_score(y_truth,y_score)
    return ndcgValue

# Testing the sample query NDGC scores for which results were calculated in query.py and index.py
def test():
    test_sampleQueries = ['life and learning']
    actualResults = ['1','3']
    with open('test_index') as fp:
            test_data = json.load(fp)
    with open('test_tfidf') as tfidfFile:
            test_tfidf = json.load(tfidfFile)
    for i in range(len(test_sampleQueries)):
        test_bool = booleanQuery(test_data, test_sampleQueries[i], 'boolean')
        print('Boolean Results: ' + str(test_bool))
        test_ndcg_score_bool = calculate_ndgc5(test_bool, actualResults, 'boolean' )
        test_vector = vectorQuery(test_data, test_sampleQueries[i], test_tfidf,'vector',3)
        print('Vector Results:  ' + str(test_vector[:5]))
        test_ndcg_score_vector = calculate_ndgc5( test_vector,actualResults, 'boolean' )
    print('Average NDCG score for Boolean Model is  ' + str(test_ndcg_score_bool))
    print('Average NDCG score for Vector Model is   ' + str(test_ndcg_score_vector))

if __name__ == '__main__':
    sampleQueries = []
    f = open(sys.argv[3])
    file = loadCranQry(sys.argv[2])
    with open(sys.argv[1]) as fp:
            data = json.load(fp)
    with open('tfidf') as tfidfFile:
            tfidf = json.load(tfidfFile)
    queryIds = list(file.keys())
    count = int(sys.argv[4])
    querySamples = random.choices(queryIds, k=count)
    querySamples = list(set(querySamples))
    print(querySamples)
    for i in querySamples:
        sampleQueries.append(file[i].text)
    querydict = {}
    mappingDict = {}
    for i in f:
        j = i.split()
        if j[0] in querydict.keys():
            querydict[j[0]].append(j[1])
        else:
            querydict[j[0]] = []
            querydict[j[0]].append(j[1])
    n = 1
    for i in file.keys():
        mappingDict[i] = []
        mappingDict[i] = querydict[str(n)]
        n += 1
    eval()
    print('====== Working on Test results =======')
    test_sampleQueries = ['life and learning']
    test_mappingDict = {'0' : [1,3]}
    test()
