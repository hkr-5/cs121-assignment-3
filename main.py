import time
import json
from nltk.stem import PorterStemmer

''' GLOBAL VARIABLES '''
ps = PorterStemmer()
indexOfIndex = {}
documentIDToURL = json.load(open('docIDToURL.json', 'r'))

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
    global documnentIDToURL
    global indexOfIndex
    
    # stem all the terms before querying
    terms = [ps.stem(term) for term in terms]

    validDocIDs = set()
    tempDocIDs = set()
            
    # new remove invalid search terms
    for term in terms:
        if term not in indexOfIndex:
            terms.remove(term)
        
    # new gets all the valid docIDs, using AND only
    for term in terms:
        with open('mergedIndex.txt', 'r') as file:
            file.seek(indexOfIndex[term])
            line = file.readline()
            
            word = line.strip().split(':')[0]
            listOfTuples = eval(line.strip().split(':')[1])
            
            for docID, termFreq in listOfTuples:
                tempDocIDs.add(docID) 
            if validDocIDs == set():
                validDocIDs = tempDocIDs
                tempDocIDs = set()
                continue
            
            validDocIDs = validDocIDs.intersection(tempDocIDs)
            tempDocIDs = set()
                    
    # new find a match and calculate the sum of frequency for each page
    hit = {}
    for term in terms:
        with open('mergedIndex.txt', 'r') as file:
            file.seek(indexOfIndex[term])
            line = file.readline()
            
            word = line.strip().split(':')[0]
            listOfTuples = eval(line.strip().split(':')[1])
            
            for docID, termFreq in listOfTuples:
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
        print('Rank', rank + 1, ':', documentIDToURL[str(hit[rank][0])])
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
                print('Time taken:', (end - start), 'seconds')

if __name__ == '__main__':
    # indexing the merged index
    createIndexOfIndex()
    
    # user input
    promptUser()
