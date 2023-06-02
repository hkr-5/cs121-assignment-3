import zipfile
import json
import os, os.path
import re
import sys
import nltk
import time
import math
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
nltk.download('punkt')

''' GLOBAL VARIABLES '''
ps = PorterStemmer()
invertedIndex = defaultdict(list)
documentIDToURL = {}
indexOfIndex = {}
documentID = 0
fileNum = 1
fileName = "offload" + str(fileNum) + ".txt"
TF = open("tempFiles.txt", 'w')

''' HELPER FUNCTIONS '''
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

def removeUrlFragment(url):
    if "#" in url:
        url = url.split("#")[0]
    return url
        
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

def dumpDataStructures():
    global documentIDToURL
    global indexOfIndex
    
    with open("docIDToURL.json", "w") as file:
        json.dump(documentIDToURL, file)
        
    with open('indexOfIndex.json', 'w') as file:
        json.dump(indexOfIndex, file)

def cleanUp():
    print('Cleaning up...')
    directory = os.getcwd()

    for filename in os.listdir(directory):
        if filename.startswith('offload') and filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"Deleted file: {filename}")
        if filename.startswith('tempFiles') and filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"Deleted file: {filename}")
        
''' MAIN FUNCTIONS FOR BUILDING INVERTED INDEX '''
def buildPartialIndexes(path):
    global invertedIndex
    global documentIDToURL
    global documentID
    global fileNum 
    global fileName 
    
    # iterate over all the files in the zip folder
    with zipfile.ZipFile(path, 'r') as zipFile:
        for zipInfo in zipFile.infolist():
            
            # check if the files are json files
            if zipInfo.filename.endswith('.json'):
                seenWords = set()
                documentID += 1
                
                # If inverted index length is greater than 10000 we offload it
                # and init a new clean dictionary to work on
                if len(invertedIndex) > 100000:
                    currFile = open(fileName, "w", encoding='utf-8')
                    for word in sorted(invertedIndex.keys()):  
                        currFile.write(word + ": " + str(invertedIndex[word]) + "\n")
                    invertedIndex.clear()
                    currFile.close()
                    TF.write(fileName + '\n')
                    fileNum += 1
                    fileName = "offload" + str(fileNum) + ".txt"
                    
                # open the json file
                with zipFile.open(zipInfo) as jsonFile:
                    # load the json file into a dictionary
                    data = json.load(jsonFile)
                    # IMPORTANT TEXT dictionary
                    wf = defaultdict(int)
                    
                    # defragment url
                    data['url'] = removeUrlFragment(data['url'])
                    
                    # check if url does not end with .pdf, .txt. php, .ff
                    if (data['url'].endswith('.pdf') or data['url'].endswith('.txt') or
                        data['url'].endswith('.php') or data['url'].endswith('.ff')):
                        continue
                    
                    print(documentID, data['url'])
                    
                    try:
                        # parse the html content
                        soup = BeautifulSoup(data['content'], 'lxml')
                    except Exception:
                        continue
                    
                    # get text from the html content
                    text = soup.get_text()
                    # tokenize the text
                    # words = re.findall(r"[a-zA-Z0-9]+", text.lower())
                    words = word_tokenize(text.lower())
                    words = [word for word in words if re.match(r'^[a-zA-Z0-9]+$', word)]
                    # stem all the word adding into index
                    words = [ps.stem(word) for word in words] 
                    
                    # iterate over the words to build the inverted index
                    for word in words: 
                        if word in seenWords:
                            continue
                        seenWords.add(word)
                        
                        wordFrequency = words.count(word)
                        
                        # add to inverted index and documentIDToURL
                        invertedIndex[word].append((documentID, wordFrequency))
                        documentIDToURL[documentID] = data['url']
                    
                    # IMPORTANT TEXT
                    for heading in soup.find_all(["a", "b", "title", "strong", "h1", "h2", "h3", "h4", "h5", "h6"]):
                        for wo in heading.text.strip().split():
                            pat = re.compile('[a-zA-Z0-9]+')
                            w = pat.findall(wo.lower())
                            if w:
                                for pw in w:
                                    wf[ps.stem(pw)] += 100
                    for word in wf:
                        invertedIndex[word].append((documentID, wf[word]))
            
            # write data to files
            # writeToFile()
            
        # offload the remaining inverted index
        currFile = open(fileName, "w", encoding='utf-8')
        for word in sorted(invertedIndex.keys()):   
            currFile.write(word + ": " + str(invertedIndex[word]) + "\n")
        invertedIndex.clear()
        currFile.close()
        TF.write(fileName + '\n')
        fileNum += 1
        fileName = "offload" + str(fileNum) + ".txt"
        
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
  
def mergePartialIndexes():
    print("Merging partial indexes...")
    TF.close()
    mergeFile = "mergedIndex.txt"
    f1 = open(mergeFile, "w")
    f1.close()
    ff = open("tempFiles.txt", 'r')
    for i in ff.readlines():
        print(f'Merging {i.strip()}')
        start = time.time()
        merge(mergeFile, i.strip())
        end = time.time()
        print(f'Merged {i.strip()} in {end-start} seconds')
    ff.close()
        
if __name__ == '__main__':
    # building the inverted index
    path = "./data/analyst.zip"
    buildPartialIndexes(path)
    
    # merge the partial indexes
    mergePartialIndexes()
    
    # indexing the merge index
    createIndexOfIndex()
    
    # dump the data structures to disk
    dumpDataStructures()

    # delete the temporary and offloaded files
    cleanUp()