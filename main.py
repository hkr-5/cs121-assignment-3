import time
import json
from nltk.stem import PorterStemmer

''' GLOBAL VARIABLES '''
ps = PorterStemmer()
indexOfIndex = json.load(open('indexOfIndex.json', 'r'))
documentIDToURL = json.load(open('docIDToURL.json', 'r'))
            
''' FUNCTIONS FOR QUERYING '''
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
            file.seek(int(indexOfIndex[term]))
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
            file.seek(int(indexOfIndex[term]))
            line = file.readline()
            
            word = line.strip().split(':')[0]
            listOfTuples = eval(line.strip().split(':')[1])
            
            for docID, termTfIdf in listOfTuples:
                if docID in validDocIDs:
                    if docID in hit:
                        hit[docID] *= termTfIdf
                    else: 
                        hit[docID] = termTfIdf
    
    # sort in descending order based on frequency 
    hit = sorted(hit.items(), key=lambda item:item[1], reverse=True)
    
    # print out top 10 hits
    # remove any duplicate pages
    rank = []
    numOfHit = len(hit)
    i = 0
    while len(rank) < 10 and len(rank) < numOfHit:
        if documentIDToURL[str(hit[i][0])] not in rank:
            rank.append(documentIDToURL[str(hit[i][0])])
            numOfHit -= 1
        i += 1
    
    for temp in range(len(rank)):
        print('Rank', temp + 1, ':', rank[temp])
    
    if rank == []:
        print('NO URL HITS')

def promptUser():
    quit = False
    print('-' * 30,  'Welcome', '-' * 30)
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
                print('Query time:', (end - start), 'seconds')

if __name__ == '__main__':    
    # user input
    promptUser()
