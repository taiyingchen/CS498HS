from collections import defaultdict
from math import exp
import sys


def read_input(filename):
    """Read input from file, return a list o links and queries
    """
    inputs = []
    
    with open(filename, 'r') as file:
        num_lines = int(file.readline())
        for _ in range(num_lines):
            user, ad, score = file.readline().split(',')
            user, ad, score = int(user), int(ad), float(score)
            inputs.append((user, ad, score))

        query_user, query_ad = file.readline().split(',')
        query_user, query_ad = int(query_user), int(query_ad)
        
    return inputs, query_user, query_ad


def parse_intput(inputs):
    """Parse input and store links in dictionary
    """
    users = set()
    ads = set()
    user_links = defaultdict(lambda: defaultdict(float))
    ad_links = defaultdict(lambda: defaultdict(float))

    for (user, ad, score) in inputs:
        users.add(user)
        ads.add(ad)
        user_links[user][ad] = score
        ad_links[ad][user] = score
    
    return users, ads, user_links, ad_links


def simrank(users, ads, user_links, ad_links, iteration, C1, C2):
    """Implementation of SimRank algorithm

    Parameters
    ----------
    users : set or list
        All user id
    ads : set or list
        All ad id
    user_links : {user: {ad: link score}}
        Link information for each user
    ad_links : {ad: {user: link score}}
        Link information for each ad
    iteration : int
        Number of iteration
    C1 : float
        A constant between 0 and 1 for user
    C2 : float
        A constant between 0 and 1 for ad
    """
    user_sim = defaultdict(lambda: defaultdict(float))
    ad_sim = defaultdict(lambda: defaultdict(float))

    # Initialize: similarity of a node to itself is 1 and 0 to all others
    for u1 in users:
        for u2 in users:
            if u1 == u2:
                user_sim[u1][u2] = 1.0
            else:
                user_sim[u1][u2] = 0.0

    for a1 in ads:
        for a2 in ads:
            if a1 == a2:
                ad_sim[a1][a2] = 1.0
            else:
                ad_sim[a1][a2] = 0.0
    
    user_list = list(users)
    ad_list = list(ads)
    # Iterative procedure
    for _ in range(iteration):
        # User similarity updates
        for i in range(len(user_list)):
            for j in range(i+1, len(user_list)):
                accum_sim = 0.0
                u1, u2 = user_list[i], user_list[j]
                for a1 in user_links[u1]:
                    for a2 in user_links[u2]:
                        accum_sim += ad_sim[a1][a2]
                user_sim[u1][u2] = C1 / (len(user_links[u1])*len(user_links[u2])) * accum_sim
                user_sim[u2][u1] = user_sim[u1][u2]

        # Ad similarity updates
        for i in range(len(ad_list)):
            for j in range(i+1, len(ad_list)):
                accum_sim = 0.0
                a1, a2 = ad_list[i], ad_list[j]
                for u1 in ad_links[a1]:
                    for u2 in ad_links[a2]:
                        accum_sim += user_sim[u1][u2]
                ad_sim[a1][a2] = C2 / (len(ad_links[a1])*len(ad_links[a2])) * accum_sim
                ad_sim[a2][a1] = ad_sim[a1][a2]

    return user_sim, ad_sim


def simrank_partial_sums(users, ads, user_links, ad_links, iteration, C1, C2):
    """Implementation of partial sums memoization version of SimRank algorithm
    Reference: https://en.wikipedia.org/wiki/SimRank#cite_note-simrank_plusplus-1

    Parameters
    ----------
    users : set or list
        All user id
    ads : set or list
        All ad id
    user_links : {user: {ad: link score}}
        Link information for each user
    ad_links : {ad: {user: link score}}
        Link information for each ad
    iteration : int
        Number of iteration
    C1 : float
        A constant between 0 and 1 for user
    C2 : float
        A constant between 0 and 1 for ad
    """
    user_sim = defaultdict(lambda: defaultdict(float))
    ad_sim = defaultdict(lambda: defaultdict(float))

    # Initialize: similarity of a node to itself is 1 and 0 to all others
    for u1 in users:
        for u2 in users:
            if u1 == u2:
                user_sim[u1][u2] = 1.0
            else:
                user_sim[u1][u2] = 0.0

    for a1 in ads:
        for a2 in ads:
            if a1 == a2:
                ad_sim[a1][a2] = 1.0
            else:
                ad_sim[a1][a2] = 0.0
    
    user_list = list(users)
    ad_list = list(ads)

    user_partial = defaultdict(lambda: defaultdict(float))
    ad_partial = defaultdict(lambda: defaultdict(float))

    # Iterative procedure
    for _ in range(iteration):
        # User similarity updates
        for a in user_list:
            for j in ad_list:
                accum_sim = 0.0
                for i in user_links[a]:
                    accum_sim += ad_sim[i][j]
                user_partial[a][j] = accum_sim
        
        for i in range(len(user_list)):
            for k in range(i+1, len(user_list)):
                accum_sim = 0.0
                a, b = user_list[i], user_list[k]
                for j in user_links[b]:
                    accum_sim += user_partial[a][j]
                user_sim[a][b] = C1 / (len(user_links[a])*len(user_links[b])) * accum_sim
                user_sim[b][a] = user_sim[a][b]

        # Ad similarity updates
        for a in ad_list:
            for j in user_list:
                accum_sim = 0.0
                for i in ad_links[a]:
                    accum_sim += user_sim[i][j]
                ad_partial[a][j] = accum_sim

        for i in range(len(ad_list)):
            for k in range(i+1, len(ad_list)):
                accum_sim = 0.0
                a, b = ad_list[i], ad_list[k]
                for j in ad_links[b]:
                    accum_sim += ad_partial[a][j]
                ad_sim[a][b] = C2 / (len(ad_links[a])*len(ad_links[b])) * accum_sim
                ad_sim[b][a] = ad_sim[a][b]

    return user_sim, ad_sim


def evidence_geometric(sim, links):
    """Revise similarity from SimRank using geometric evidence score
    Reference: https://arxiv.org/pdf/0712.0499.pdf
    """
    nodes = list(sim.keys())
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            a, b = nodes[i], nodes[j]
            edge_a = set(links[a].keys())
            edge_b = set(links[b].keys())

            evidence = 0
            for k in range(1, len(edge_a.intersection(edge_b))+1):
                evidence += 1 / (2**k)
            
            sim[a][b] *= evidence
            sim[b][a] = sim[a][b]
    
    return sim


def evidence_exponential(sim, links):
    """Revise similarity from SimRank using exponential evidence score
    Reference: https://arxiv.org/pdf/0712.0499.pdf
    """
    nodes = list(sim.keys())
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            a, b = nodes[i], nodes[j]
            edge_a = set(links[a].keys())
            edge_b = set(links[b].keys())

            evidence = 1 - exp(-len(edge_a.intersection(edge_b)))
            
            sim[a][b] *= evidence
            sim[b][a] = sim[a][b]

    return sim


def sort_query_result(sim, query):
    result = [(node, round(value, 4)) for node, value in sim[query].items() if node != query]
    # First sorted by value then sorted by id
    result = sorted(result, key=lambda k: (-k[1], k[0]))

    unique_result = []
    value_set = set()
    for node, value in result:
        if value not in value_set:
            value_set.add(value)
            unique_result.append((node, value))
    return unique_result


def output_result(output, filename):
    with open(filename, 'w') as file:
        for row in output:
            file.write(row + '\n')


def main(argv):
    input_filename = argv[1]
    output_filename = argv[2]

    iteration = 10
    C1, C2 = 0.8, 0.8
    topk = 3
    inputs, query_user, query_ad = read_input(input_filename)
    users, ads, user_links, ad_links = parse_intput(inputs)

    # Run SimRank algorithm
    user_sim, ad_sim = simrank(users, ads, user_links, ad_links, iteration, C1, C2)

    # Output results from simple SimRank algorithm
    output = []
    result_user = sort_query_result(user_sim, query_user)
    result_query = sort_query_result(ad_sim, query_ad)
    output.append(','.join([str(k) for k, v in result_user[:topk]]))
    output.append(','.join([str(k) for k, v in result_query[:topk]]))

    # Output results of geometric evidence scores
    user_sim_geo = evidence_geometric(user_sim.copy(), user_links)
    ad_sim_geo = evidence_geometric(ad_sim.copy(), ad_links)
    result_user = sort_query_result(user_sim_geo, query_user)
    result_query = sort_query_result(ad_sim_geo, query_ad)
    output.append(','.join([str(k) for k, v in result_user[:topk]]))
    output.append(','.join([str(k) for k, v in result_query[:topk]]))

    # Output results of exponential evidence scores
    user_sim_exp = evidence_exponential(user_sim.copy(), user_links)
    ad_sim_exp = evidence_exponential(ad_sim.copy(), ad_links)
    result_user = sort_query_result(user_sim_exp, query_user)
    result_query = sort_query_result(ad_sim_exp, query_ad)
    output.append(','.join([str(k) for k, v in result_user[:topk]]))
    output.append(','.join([str(k) for k, v in result_query[:topk]]))

    # Output all results to file
    output_result(output, output_filename)


if __name__ == "__main__":
    main(sys.argv)
