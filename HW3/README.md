# Homework 3: SimRank Algorithm Implementation

You are required to implement the SimRank algorithm and SimRank with two forms of evidence weights in a programming language of your choice. In each case, your iterations must begin with user updates, alternating with ad similarity updates. We will use this reference[https://arxiv.org/pdf/0712.0499.pdf] for the algorithm details. We provide two test cases (a) and (b) as input. You can use the sample test case (a), which is smaller in size, to debug your code. The test case (b) is significantly larger and hence may require an efficient implementation. Thus, you should use partial sum sharing to speed up your implementation.

The input consists of weighted User-Ad links. The first line specifies the total number of links $N$, followed by $N$ lines each containing three comma separated entries - $U,A,S$ where $U$ and $A$ are integers representing User and Ad Ids, $0 ≤ U ≤ 1,000,000$ and $0 ≤ A ≤ 1, 000, 000$, and score $S$ is a float score value for that link, $0.0 ≤ S ≤ 1, 000.0$. The score is based on how fast the user responded to the Ad (a higher score denotes a greater proclivity).

This is then followed by a single line with two ids, $Q_U$ and $Q_A$. You need to output the three most similar users to $Q_U$ and the three most similar ads to $Q_A$ with each of the variations of simrank. In case of a tie break, report all users (ads). A sample input looks like:

$$
N
U_1,A_1,S_1\\
U_2,A_2,S_2\\
...\\
U_N,A_N,S_N\\
Q_U,Q_A\\
$$

Note $U_1$ is a user-id, while $A_1$ is the advertisement-id for a specific ad clicked by $U_1$ and $S_1$ is the link weight. Note that a given user can click more than one ad, meaning multiple lines could have the same user-id, but no two lines are identical. You are required to build the bipartite weighted User-Ad graph using the above links.

## Programming Language

Python 3.7

## Usage

```bash
python3 simrank.py INPUT_FILENAME OUTPUT_FILENAME
```

### Example

```bash
python3 simrank.py input_b.txt output.txt
```

## Descriptions

### `simrank`

Function `simrank` is an implentation of SimRank algorithm from the original paper [SimRank: A Measure of Structural-Context Similarity](http://ilpubs.stanford.edu:8090/508/1/2001-41.pdf). In each iteration it alternatively updates the user similarity the ad similarity with the following formula. Its time complexity is $O(Kd^2n^2)$, where $K$ is the number of iterations, $d$ is average degree of a graph, and $n$ is the number of nodes in a graph.

$$
s(q,q') = \frac{C_1}{N(q)N(q')}\sum_{i\in E(q)}\sum_{j\in E(q')}s(i,j)
$$

$$
s(\alpha,\alpha') = \frac{C_2}{N(\alpha)N(\alpha')}\sum_{i\in E(\alpha)}\sum_{j\in E(\alpha')}s(i,j)
$$

Where $q,q'$ are users and $\alpha,\alpha'$ are ads.

### `simrank_partial_sums`

Function `simrank_partial_sums` is an implementation of partial sums memoization version of SimRank algorithm from [Accuracy Estimate and Optimization Techniques for SimRank Computation](https://en.wikipedia.org/wiki/SimRank#cite_note-simrank_plusplus-1). It speeds up the computation of SimRank from $O(Kd^2n^2)$ to $O(Kdn^2)$, where $K$ is the number of iterations, $d$ is average degree of a graph, and $n$ is the number of nodes in a graph. The central idea of partial sums memoization consists of two steps:

First, the partial sums over $I(\alpha)$ are memoized as

$$
\text{Partial}^{s_k}_{I(\alpha)}(j)=\sum_{i\in I(\alpha)}s_k(i, j)
$$

and then $s_{k+1}(a,b)$ is iteratively computed from $\text{Partial}^{s_k}_{I(\alpha)}(j)$ as

$$
s_{k+1}(a,b) = \frac{C}{|I(a)||I(b)|}\sum_{j\in I(b)}\text{Partial}^{s_k}_{I(\alpha)}(j)
$$

Consequently, the results of $\text{Partial}^{s_k}_{I(\alpha)}(j)$, $\forall j\in I(b)$, can be reused later when we compute the similarities $s_{k+1}(\alpha, *)$ for a given vertex $\alpha$ as the first argument.

## Analysis

To compare these two implementation of SimrRank, I run a shell script `time.sh` which runs `simrank.py` with two implementation for 100 times. The elasping time results are as follows:

| Type      | `simrank` | `simrank_partial_sums` |
|-----------|:---------:|:----------------------:|
| real      | 6m2.197s  | 5m54.006s              |
| user      | 5m57.649s | 5m49.573s              |
| sys       | 0m2.773s  | 0m2.806s               |
| avg. real | 0m3.622s  | 0m3.540s               |
| avg. user | 0m3.576s  | 0m3.496s               |
| avg. sys  | 0m0.028s  | 0m0.028s               |