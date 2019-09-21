import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import sys


def read_nodes(filename):
    node2category = {}
    category2node = defaultdict(list)
    with open(filename, 'r') as file:
        for row in file:
            index, category = row.split()
            node2category[index] = category
            category2node[category].append(index)
    return node2category, category2node


def read_edges(filename):
    edges = []
    with open(filename, 'r') as file:
        for row in file:
            node1, node2 = row.split()
            edges.append((node1, node2))
    return edges


def create_graph(edges):
    G = nx.DiGraph()
    G.add_edges_from(edges)
    return G


def main(argv):
    nodes_filename = argv[1]
    edges_filename = argv[2]
    query = argv[3]
    node2category, category2node = read_nodes(nodes_filename)
    edges = read_edges(edges_filename)
    G = create_graph(edges)

    # Calculate the PageRank with damping parameter = 1
    pr = nx.pagerank(G, alpha=1.0)

    # Print out all PageRank result
    sorted_pr = sorted(pr.items(), key=lambda k: k[1], reverse=True)
    print('No.\tNode\tValue')
    for index, (node, value) in enumerate(sorted_pr):
        print(index+1, '\t', node, '\t', value)

    # List nodes related to the query
    query_nodes = category2node[query]
    query_pagerank = []
    for node in query_nodes:
        query_pagerank.append((node, pr[node]))

    # Sort in decreasing order
    query_pagerank = sorted(query_pagerank, key=lambda k: k[1], reverse=True)

    # Print out the result
    print('No.\tNode\tValue')
    for index, (node, value) in enumerate(query_pagerank):
        print(index+1, '\t', node, '\t', value)

    # Plot the graph
    nx.draw(G, with_labels=True)
    plt.show()


if __name__ == "__main__":
    main(sys.argv)
