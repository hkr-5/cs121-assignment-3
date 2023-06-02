import time
import json
from nltk.stem import PorterStemmer

''' GLOBAL VARIABLES '''
ps = PorterStemmer()
indexOfIndex = {}

''' HELPER FUNCTIONS '''
def createIndexOfIndex():
    global indexOfIndex
    
    with open('mergedIndex.txt', 'r') as f:
        offset = f.tell()
        line = f.readline()
        word = line.strip().split(':')[0]
        indexOfIndex[word] = offset
        
        while line:
            offset = f.tell()
            line = f.readline()
            word = line.strip().split(':')[0]
            indexOfIndex[word] = offset
            
''' FUNCTIONS FOR QUERYING '''
# retrieve does not work yet!
def retrieve(terms):
    # stem all the terms before querying
    terms = [ps.stem(term) for term in terms]

    validDocIDs = set()
    tempDocIDs = set()

    # remove invalid search terms
    for term in terms:
        if term not in invertedIndex:
            terms.remove(term)

    # gets all the valid docIDs, using AND only
    for term in terms:
        for docID, termFreq in invertedIndex[term]:
            tempDocIDs.add(docID)
        if validDocIDs == set():
            validDocIDs = tempDocIDs
            tempDocIDs = set()
            continue
        validDocIDs = validDocIDs.intersection(tempDocIDs)
        tempDocIDs = set()

    # find a match and calculate the sum of frequency for each page
    hit = {}
    for term in terms:
        for docID, termFreq in invertedIndex[term]:
            if docID in validDocIDs:
                if docID in hit:
                    hit[docID] = hit[docID] + termFreq
                else: 
                    hit[docID] = termFreq
    
    # sort in descending order based on frequency 
    hit = sorted(hit.items(), key=lambda item:item[1], reverse=True)
    
    # print out top 5 hits
    rank = 0
    while rank < 5 and rank < len(hit):
        print('Rank', rank + 1, ':', documentIDToURL[hit[rank][0]])
        rank += 1

def promptUser():
    quit = False
    print('-' * 10,  'Welcome', '-' * 10)
    while (not quit):
        searchTerm = input('Please Enter Search Term (enter \'*\' to quit): ')
        if searchTerm == '*':
            print("Terminating search session. See you next time!")
            quit = True
        else:
            searchTerm = searchTerm.lower().strip()
            if len(searchTerm) == 0:
                print('Error: Please enter a valid term.')
            else:
                searchTerm = searchTerm.split(' ')
                start = time.time()
                retrieve(searchTerm)
                end = time.time()
                print('Time taken:', (end - start)//1000, 'milliseconds')

if __name__ == '__main__':
    # indexing the merged index
    createIndexOfIndex()
    
    # user input
    promptUser()
