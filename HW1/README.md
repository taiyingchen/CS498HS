# Homework 1

The objective of the programming assignment is to give you a better understanding of page rank. We have provided you two graphs with 100 nodes each. You can find the list of the node ids and their categories in the file nodes.txt. The edges for the graphs can be found in the files network1 edges.txt and network2 edges.txt respectively.

Apply the page rank algorithm on the graphs separately for 100 iterations. You are free to use methods from existing libraries like NetworkX (https://networkx.github.io), SNAP (https://snap.stanford.edu/snappy/), etc.

## Programming Language

Python 3.6

## Requirements

```bash
pip install networkx
pip install matplotlib
```

## Usage

### Example

`query.py`

```bash
python query.py NODE_FILE_NAME EDGE_FILE_NAME CATEGORY
```

`plot.py`

```bash
python plot.py NODE_FILE_NAME EDGE_FILE_NAME NODE_ID
```

### Usage for Programming Questions

1. For a search query on category Sports, list out the top-10 nodes in decreasing order of pagerank for network1.

```bash
python query.py nodes.txt network1_edges.txt sports
```

2. For a search query on category Politics, list out the top-10 nodes in decreasing order
of pagerank for network2.

```bash
python query.py nodes.txt network2_edges.txt politics
```

3. Plot a graph showing the variation in page rank value of node with id 2 for network1
over 100 iterations.

```bash
python plot.py nodes.txt network1_edges.txt 2
```

4. Plot a graph showing the variation in page rank value of node with id 2 for network2 over 100 iterations.

```bash
python plot.py nodes.txt network2_edges.txt 2
```