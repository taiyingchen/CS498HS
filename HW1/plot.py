import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import sys


"""
This pagerank function is modified from the source code below
- NetworkX 
- April 2019
- PageRank source code
- Code version 2.3
- https://networkx.github.io
"""
def pagerank(G, alpha=0.85, personalization=None,
             max_iter=100, tol=1.0e-6, nstart=None, weight='weight',
             dangling=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.

    Parameters
    ----------
    G : graph
      A NetworkX graph.  Undirected graphs will be converted to a directed
      graph with two directed edges for each undirected edge.

    alpha : float, optional
      Damping parameter for PageRank, default=0.85.

    personalization: dict, optional
      The "personalization vector" consisting of a dictionary with a
      key some subset of graph nodes and personalization value each of those.
      At least one personalization value must be non-zero.
      If not specfiied, a nodes personalization value will be zero.
      By default, a uniform distribution is used.

    max_iter : integer, optional
      Maximum number of iterations in power method eigenvalue solver.

    tol : float, optional
      Error tolerance used to check convergence in power method solver.

    nstart : dictionary, optional
      Starting value of PageRank iteration for each node.

    weight : key, optional
      Edge data key to use as weight.  If None weights are set to 1.

    dangling: dict, optional
      The outedges to be assigned to any "dangling" nodes, i.e., nodes without
      any outedges. The dict key is the node the outedge points to and the dict
      value is the weight of that outedge. By default, dangling nodes are given
      outedges according to the personalization vector (uniform if not
      specified). This must be selected to result in an irreducible transition
      matrix (see notes under google_matrix). It may be common to have the
      dangling dict to be the same as the personalization dict.

    Returns
    -------
    pagerank : dictionary
       Dictionary of nodes with PageRank as value

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(4))
    >>> pr = nx.pagerank(G, alpha=0.9)

    Notes
    -----
    The eigenvector calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop after
    an error tolerance of ``len(G) * tol`` has been reached. If the
    number of iterations exceed `max_iter`, a
    :exc:`networkx.exception.PowerIterationFailedConvergence` exception
    is raised.

    The PageRank algorithm was designed for directed graphs but this
    algorithm does not check if the input graph is directed and will
    execute on undirected graphs by converting each edge in the
    directed graph to two edges.

    See Also
    --------
    pagerank_numpy, pagerank_scipy, google_matrix

    Raises
    ------
    PowerIterationFailedConvergence
        If the algorithm fails to converge to the specified tolerance
        within the specified number of iterations of the power iteration
        method.

    References
    ----------
    .. [1] A. Langville and C. Meyer,
       "A survey of eigenvector methods of web information retrieval."
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry,
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf

    """
    if len(G) == 0:
        return {}

    if not G.is_directed():
        D = G.to_directed()
    else:
        D = G

    # Create a copy in (right) stochastic form
    W = nx.stochastic_graph(D, weight=weight)
    N = W.number_of_nodes()

    # Choose fixed starting vector if not given
    if nstart is None:
        x = dict.fromkeys(W, 1.0 / N)
    else:
        # Normalized nstart vector
        s = float(sum(nstart.values()))
        x = dict((k, v / s) for k, v in nstart.items())

    if personalization is None:
        # Assign uniform personalization vector if not given
        p = dict.fromkeys(W, 1.0 / N)
    else:
        s = float(sum(personalization.values()))
        p = dict((k, v / s) for k, v in personalization.items())

    if dangling is None:
        # Use personalization vector if dangling vector not specified
        dangling_weights = p
    else:
        s = float(sum(dangling.values()))
        dangling_weights = dict((k, v / s) for k, v in dangling.items())
    dangling_nodes = [n for n in W if W.out_degree(n, weight=weight) == 0.0]

    # power iteration: make up to max_iter iterations
    x_hist = []
    for _ in range(max_iter):
        xlast = x
        x = dict.fromkeys(xlast.keys(), 0)
        danglesum = alpha * sum(xlast[n] for n in dangling_nodes)
        for n in x:
            # this matrix multiply looks odd because it is
            # doing a left multiply x^T=xlast^T*W
            for nbr in W[n]:
                x[nbr] += alpha * xlast[n] * W[n][nbr][weight]
            x[n] += danglesum * dangling_weights.get(n, 0) + (1.0 - alpha) * p.get(n, 0)
        # check convergence, l1 norm
        # err = sum([abs(x[n] - xlast[n]) for n in x])
        # if err < N * tol:
        #     return x
        x_hist.append(x.copy())
    return x_hist
    # raise nx.PowerIterationFailedConvergence(max_iter)


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
    node_id = argv[3]
    node2category, category2node = read_nodes(nodes_filename)
    edges = read_edges(edges_filename)
    G = create_graph(edges)

    # Calculate the PageRank with damping parameter = 1
    pr_history = pagerank(G, alpha=1.0)

    # Print out the result
    pr_plot = []
    print('Iteration\tValue')
    for index, pr in enumerate(pr_history):
        pr_plot.append(pr[node_id])
        print(index+1, '\t', pr[node_id])

    # Plot the graph
    plt.plot(range(len(pr_plot)), pr_plot, marker='o', markersize=4)
    plt.xlabel('Iteration')
    plt.ylabel('Page Rank Value')
    plt.title(f'Page Rank value of node with id {node_id} for {edges_filename}')
    plt.show()


if __name__ == "__main__":
    main(sys.argv)
