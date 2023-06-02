# Search Engine

### Installation
To the run the program, make sure to have the latest version of Python installed as well as the following dependencies:
- BeautifulSoup: pip install bs4
- NLTK: pip install nltk

### How to Run Indexer
Have the zip folder of all the crawled urls inside a folder labeled data. Make sure the data folder is at the root of the project directory (same location as main.py and index.py). Next, navigate to the folder that contains index.py and execute the following command in the terminal.
``` 
python index.py 
```
The program will begin to build the partial inverted index, and then merge all the inverted indexes together. After running index.py, the merged index should appear as a text file named mergedIndex.txt. Another file should also be created called docIDToURL.json. 

### How to Run Search Interface
Make sure to run to the indexer if the mergedIndex.txt file is not in the project directory. Next, navigate to the folder that contains main.py and execute the following command in the terminal.
``` 
python main.py 
```
The program will begin executing and it will ask you to enter a search query. After taking your search query, it will go through the merged inverted index and return a list of highly recommended links. Below is a visual of the search interface.
![searchEngineInterface](https://github.com/hkr-5/cs121-assignment-3/assets/87344458/fae80fa1-2c07-4e88-ba43-a733b973df6b)

### Test Queries
Below are the queries we used to test during development along with comments on which ones returned poor results and what we did to make them perform better.
- master of software engineering, [insert comment here]
- cristina lopes, [insert comment here]
- machine learning, [insert comment here]
- ACM, [insert comment here]
- students, [insert comment here]
- professors, [insert comment here]
- computer science, [insert comment here]
- classes, [insert comment here]
- coursework, [insert comment here]
- industry, [insert comment here]
- professor thornton, [insert comment here]
- student council, [insert comment here]
- academic advisor, [insert comment here]
- counselors, [insert comment here]
- computers, [insert comment here]
- machines, [insert comment here]
- ICS, [insert comment here]
- servers, [insert comment here]
- anteaters, [insert comment here]
- scooters, [insert comment here]
- law enforcement, [insert comment here]
