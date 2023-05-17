import zipfile
import json
import os
import re
import sys
import nltk
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
nltk.download('stopwords')

''' 
REPORT
- number of indexed documents
- number of unique words
- total size (in KB) of index on disk
'''

# REMINDERS: stem the words before adding to inverted index, dump the partial inverted indexes onto disk
# MAKE SURE TO HAVE EITHER developer.zip or analyst.zip in the same directory as this file
# RUN PIP INSTALL LXML to install lxml parser

''' GLOBAL VARIABLES '''
invertedIndex = defaultdict(list)
documentIDToURL = {}
documentID = 0
partList = list()
fileNum = 1
fileName = "offload" + str(fileNum) + ".txt"

def writeToFile():
    global invertedIndex
    global documentIDToURL
    global documentID
    
    # write the number of indexed documents to a file
    with open('numberOfIndexedDocuments.txt', 'w') as f:
        f.write(f"Number of Indexed Documents: {documentID}")
        
    # write the number of unique words to a file
    with open('numberOfUniqueWords.txt', 'w') as f:
        f.write(f"Number of Unique Words: {len(invertedIndex)}")
        
    # write the total size of the inverted index on disk to a file
    with open('totalSizeOfIndexOnDisk.txt', 'w') as f:
        f.write(f"Total Size of Inverted Index on Disk: {sys.getsizeof(invertedIndex)//1024} kilobytes")
        
    # write the total size of the documentIDToURL on disk to a file
    with open('totalSizeOFDocumentIDToURL.txt', 'w') as f:
        f.write(f"Total Size of DocumentIDToURL on Disk: {sys.getsizeof(documentIDToURL)//1024} kilobytes")

def buildInvertedIndex(path):
    global invertedIndex
    global documentIDToURL
    global documentID
    global fileNum 
    global fileName 
    global partList
    # iterate over all the files in the zip folder
    with zipfile.ZipFile(path, 'r') as zipFile:
        for zipInfo in zipFile.infolist():
            
            
            # check if the files are json files
            if zipInfo.filename.endswith('.json'):
                seenWords = set()
                documentID += 1
                if len(invertedIndex) > 10000:
                    # If inverted index length is greater than 10000 we offload it
                    # and init a new clean dictionary to work on
                    currFile = open(fileName, "w")
                    for word in sorted(invertedIndex.keys()):   
                        currFile.write(word + ": " + str(invertedIndex[word]) + "\n")
                    partList.append(fileName)
                    invertedIndex.clear()
                    currFile.close()
                    fileNum += 1
                    fileName = "offload" + str(fileNum) + ".txt"
                
                # open the json file
                with zipFile.open(zipInfo) as jsonFile:
                    # load the json file into a dictionary
                    data = json.load(jsonFile)
                    
                    # check if url does not end with .pdf or .txt
                    if data['url'].endswith('.pdf') or data['url'].endswith('.txt'):
                        continue
                
                    try:
                        # parse the html content
                        soup = BeautifulSoup(data['content'], 'lxml')
                    except Exception:
                        continue
                    
                    # get text from the html content
                    text = soup.get_text()
                    # tokenize the text
                    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
                    # remove stop words
                    wordSet = set(words) - set(stopwords.words("english"))
                    
                    # iterate over the words to build the inverted index
                    for word in wordSet: 
                        if word in seenWords:
                            continue
                        seenWords.add(word)
                        
                        wordFrequency = words.count(word)
                        
                        # add to inverted index and documentIDToURL``
                        invertedIndex[word].append((documentID, wordFrequency))
                        documentIDToURL[documentID] = data['url']
            
            # write data to files
            writeToFile()
            

def retrieve(terms):

    terms = set(terms) - set(stopwords.words("english"))
    
    # find a match and calculate the sum of frequency for each page
    hit = {}
    for term in terms:
        if term in invertedIndex:
            for pageList in invertedIndex[term]:
                if pageList[0] in hit:
                    hit[pageList[0]] = hit[pageList[0]] + pageList[1]
                else: 
                    hit[pageList[0]] = pageList[1]
    
    # sort in descending order based on frequency 
    hit = sorted(hit.items(), key=lambda item:item[1], reverse=True)
    
    # print out top 5 hits
    rank = 0
    while rank < 5 and rank < len(hit):
        print('Rank', rank + 1, ':', documentIDToURL[hit[rank][0]])
        rank += 1
        
    
if __name__ == '__main__':
    path = "analyst.zip"
    
    buildInvertedIndex(path)
    #paths = "C:/Users/jESUS/eclipse-workspace/A3/analyst.zip"

    searchTerm = input('Search Term: ').lower().strip().split(' ')
    print(searchTerm)
    retrieve(searchTerm)
