import zipfile
import json
import os
import re
import sys
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

def buildInvertedIndex(path):
    invertedIndex = defaultdict(list)
    documentIDToURL = {}
    documentID = 0
    
    # iterate over all the files in the zip folder
    with zipfile.ZipFile(path, 'r') as zipFile:
        for zipInfo in zipFile.infolist():
            
            # check if the files are json files
            if zipInfo.filename.endswith('.json'):
                seenWords = set()
                documentID += 1
                
                # open the json file
                with zipFile.open(zipInfo) as jsonFile:
                    # load the json file into a dictionary
                    data = json.load(jsonFile)
                    
                    # parse the html content
                    soup = BeautifulSoup(data['content'], 'html.parser')
                    text = soup.get_text()
                    
                    # tokenize the text
                    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
                    
                    # iterate over the words to build the inverted index
                    for word in words: 
                        if word in seenWords:
                            continue
                        seenWords.add(word)
                        
                        wordFrequency = words.count(word)
                        
                        # add to inverted index and documentIDToURL
                        invertedIndex[word].append((documentID, wordFrequency))
                        documentIDToURL[documentID] = data['url']
                        
    # write the number of indexed documents to a file
    with open('numberOfIndexedDocuments.txt', 'w') as f:
        f.write(f"Number of Indexed Documents: {documentID}")
        
    # write the number of unique words to a file
    with open('numberOfUniqueWords.txt', 'w') as f:
        f.write(f"Number of Unique Words: {len(invertedIndex)}")
        
    # write the total size of the index on disk to a file
    with open('totalSizeOfIndexOnDisk.txt', 'w') as f:
        f.write(f"Total Size of Index on Disk: {sys.getsizeof(invertedIndex)//1024} kilobytes")
                    
    return invertedIndex

if __name__ == '__main__':
    path = 'analyst.zip'
    invertedIndex = buildInvertedIndex(path)
    print(invertedIndex)
