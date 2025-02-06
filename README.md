#PageRank
This is an implementation of the PageRank algorithm for my Web technologies class. The algorithm starts from a root site and visits every site the root links to. This continues up to a certain depth. Sites that have blocked root access in their robots.txt file are skipped. Afterwards, it calculates each site's rank and constructs a graph, showing the top 5 highest ranked sites, along with lower-ranked sites that link to them.

##Requirements
The required Python packages for running this script are the following: bs4 (4.12.3), requests (2.32.3), numpy (1.26.4), networkx (3.2.1) and matplotlib (3.9.2).

##Usage
```
python pagerank.py
```
