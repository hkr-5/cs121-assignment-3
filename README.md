# Search Engine

Team Members:
- Chris Tran, cvtran3, 47699198
- Hikaru Yamamoto, yamamoh1, 69645506
- Nam Mai, namtm, 13825230

### Installation
To the run the program, make sure to have the latest version of Python installed as well as the following dependencies:
- BeautifulSoup: pip install bs4
- NLTK: pip install nltk

### How to Run Indexer
Have the zip folder of all the crawled urls inside a folder labeled data. Make sure the data folder is at the root of the project directory (same location as main.py and index.py). Next, navigate to the folder that contains index.py and execute the following command in the terminal.
``` 
python index.py 
```
The program will begin to build the partial inverted index, and then merge all the inverted indexes together. After running index.py, the merged index should appear as a text file named mergedIndex.txt. Two other files are created called docIDToURL.json and indexOfIndex.json.

### How to Run Search Interface
Make sure to run to the indexer if the mergedIndex.txt file is not in the project directory. Next, navigate to the folder that contains main.py and execute the following command in the terminal.
``` 
python main.py 
```
The program will begin executing and it will ask you to enter a search query. After taking your search query, it will go through the merged inverted index and return a list of highly recommended links. Below is a visual of the search interface.

![SearchEngineInterface](https://github.com/hkr-5/cs121-assignment-3/assets/87344458/fa7f1d6f-35ce-4f04-aa62-e18e8333d504)

### Test Queries
Below are the queries we used to test during development along with comments on which ones returned poor results and what we did to make them perform better.
- software engineering:
Poor result initially, but improved the result by implementing the tf-idf score. Query time: 0.13317608833312988 seconds
- cristina lopes: Good result. Query time: 0.006011962890625 seconds
- machine learning: Good result. Query time: 0.023628711700439453 seconds
- ACM: Good result. Query time: 0.006910800933837891 seconds
- students: Good result. Query time: 0.04178571701049805 seconds
- professors: Good result. Query time: 0.04320335388183594 seconds
- computer science: Good result. Query time: 0.07419943809509277 seconds
- classes: Bad result initially, but improved by adding the important text factor, also used Porter stemming. Query time: 0.010414838790893555 seconds
- coursework: Bad result initially, improved by adding important text factor. Query time: 0.003992557525634766 seconds
- industry: Bad result initially because of the query time, however decreased query time to under 300ms. Query time: 0.01543116569519043 seconds
- thornton: Bad result initially because we added too much weight on the important text. Decrease important text weight from 100 to 10. Query time: 0.04150128364562988 seconds
- student council: Good result. Query time: 0.04134416580200195 seconds
- academic advisor: Bad result initially because we calculated tf-idf before index was fully created, improved by calculating index after the merging process. Query time: 0.013852357864379883 seconds
- counselors: Good result. Query time: 0.003516674041748047 seconds
- computers: Good reuslt. Query time: 0.05107426643371582 seconds
- machines: Good result. Query time: 0.007458209991455078 seconds
- ICS: Bad result initially because we weighted the important text such as heading too much by adding 100 to the tf-idf score. Improved by only adding a factor of 10. Query time: 0.015084505081176758 seconds
- servers: Bad result initially because of improper weighting on important text, and improved by decreasing weight. Query time: 0.003999233245849609 seconds
- anteaters: Good result. Query time: 0.003000020980834961 seconds
- scooters: Bad result. Query time: 0.0010073184967041016 seconds
- law: Good result. Query time: 0.003995418548583984 seconds
- seminar: Good result. Query time: 0.005245382420424324 seconds
