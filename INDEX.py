import zipfile
import json
import os, os.path
import re
import sys
import nltk
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer

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
TF = open("tempFiles.txt", 'w')

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
                
                # If inverted index length is greater than 10000 we offload it
                # and init a new clean dictionary to work on
                if len(invertedIndex) > 10000:
                    currFile = open(fileName, "w")
                    for word in sorted(invertedIndex.keys()):   
                        currFile.write(word + ": " + str(invertedIndex[word]) + "\n")
                    partList.append(fileName)
                    invertedIndex.clear()
                    currFile.close()
                    TF.write(fileName + '\n')
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
                    
                    # iterate over the words to build the inverted index
                    for word in words: 
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
    # computer science
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
        
        
def merge(mFile, tFile):
    # merge two files together
    mF = open(mFile, "r") # open merge file
    tF = open(tFile, "r") # open temp file
    mData = mF.readline()
    tData = tF.readline()
    while mData != "" or tData != "": # run the loop while at least one file is not empty
        mData11 = list()
        tData11 = list()
        mDataL = list()
        tDataL = list()
        mData = re.sub(r"(\[)*(\])*(\()*(\))*", "", mData)
        mData1 = re.sub(r":",",",mData).strip("\n").split(",") # removes {} and splits it by ,
        for i in mData1:
            mDataL.append(i.strip("'' ")) # removes extra ""
            
        tData = re.sub(r"(\[)*(\])*(\()*(\))*", "", tData)
        tData1 = re.sub(r":",",",tData).strip("\n").split(",") # removes {} and splits it by ,
        for i in tData1:
            tDataL.append(i.strip("'' ")) # removes extra ""
    
        if mData == "" and tData == "":
            pass
        elif mData == "" and tData != "":
            for i in range(1, len(tDataL),2):
                tData11.append((int(tDataL[i]), int(tDataL[i+1])))
                
            # just add the temp token info to the text file
            with open("tempMerge.txt", "a") as f:
                f.write(tDataL[0]+":"+str(tData11)+"\n")
            tData = tF.readline()
            
        elif tData == "" and mData != "":
            for i in range(1, len(mDataL), 2):
                mData11.append((int(mDataL[i]), int(mDataL[i+1])))
            # just add the merge token info to the text file
            with open("tempMerge.txt", "a") as f:
                f.write(mDataL[0]+":"+str(mData11)+"\n")
            mData = mF.readline()
        else:
            for i in range(1, len(mDataL), 2):
                mData11.append((int(mDataL[i]), int(mDataL[i+1])))
            for i in range(1, len(tDataL),2):
                tData11.append((int(tDataL[i]), int(tDataL[i+1])))
            # check if they're the same token
            if mDataL[0] != tDataL[0]:
                # if first token match is tempTok then we add tempToken to the tempMerge file
                if sorted([mDataL[0].lower(), tDataL[0].lower()])[0] != mDataL[0].lower():
                    with open("tempMerge.txt", "a") as f:
                        f.write(tDataL[0]+":"+str(tData11)+"\n")
                    tData = tF.readline()
                else:
                    # if the first token match is mergeTok then we add mergeToken to the tempMerge file
                    with open("tempMerge.txt", "a") as f:
                        f.write(mDataL[0]+":"+str(mData11)+"\n")
                    mData = mF.readline()
                
            else:
                for data in tData11:
                    mData11.append(data)
                with open("tempMerge.txt", "a") as f:
                    f.write(mDataL[0]+":"+str(mData11)+"\n")
                mData = mF.readline()
                tData = tF.readline() 
            

    mF.close()
    tF.close()
    os.remove(mFile)
    os.rename("tempMerge.txt", mFile)
        
        
if __name__ == '__main__':
    path = "analyst.zip"
    all_files = []
    buildInvertedIndex(path)
    TF.close()
    mergeFile = "merge.txt"
    f1 = open(mergeFile, "w")
    f1.close()
    ff = open("tempFiles.txt", 'r')
    Lines = ff.readlines()
    for i in Lines:
        merge(mergeFile, i.strip())
    

    quit = False
    print('-' * 10,  'Welcome', '-' * 10)
    while(not quit):
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
                retrieve(searchTerm)