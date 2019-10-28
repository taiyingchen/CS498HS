from collections import defaultdict
from math import exp
import sys


def read_input(filename):
    """Read input from file, return a list of ratings, movies' metadata, and queries
    """
    ratings = []
    queries = []
    movies = {}
    
    with open(filename, 'r') as file:
        num_ratings, num_movies = file.readline().split()
        num_ratings, num_movies = int(num_ratings), int(num_movies)
        num_queries = 5

        for _ in range(num_ratings):
            user, movie, rating = file.readline().split()
            user, movie, rating = int(user), int(movie), float(rating)
            ratings.append((user, movie, rating))

        for _ in range(num_movies):
            line = file.readline()
            try:
                movie, metadata = line.split(maxsplit=1)
            except ValueError:
                movie, metadata = int(line.split()[0]), ''

            movie = int(movie)
            metadata = metadata.strip()
            movies[movie] = metadata

        for _ in range(num_queries):
            user, movie = file.readline().split()
            user, movie = int(user), int(movie)
            queries.append((user, movie))
        
    return ratings, movies, queries


def output_result(output, filename):
    with open(filename, 'w') as file:
        for row in output:
            file.write(row + '\n')


def main(argv):
    input_filename = 'HW4/input.txt'
    # input_filename = argv[1]
    # output_filename = argv[2]

    ratings, movies, queries = read_input(input_filename)
    
    
    user_ratings = defaultdict(list)
    movie_ratings = defaultdict(list)
    global_mean = []
    for user, movie, rating in ratings:
        user_ratings[user].append((movie, rating))
        movie_ratings[movie].append((user, rating))
        global_mean.append(rating)
    global_mean = sum(global_mean) / len(ratings)

    # Estimate movie biases
    movie_biases = {}
    for movie in movie_ratings:
        # b_i = sum(r_ui - mu) / len(R(i))
        movie_bias = [rating - global_mean for user, rating in movie_ratings[movie]]
        movie_bias = sum(movie_bias) / len(movie_bias)
        movie_biases[movie] = movie_bias
    
    # Estimate user biases
    user_biases = {}
    for user in user_ratings:
        # b_u = sum(r_ui - mu - b_i) / len(R(u))
        user_bias = [rating - global_mean - movie_biases[movie] for movie, rating in user_ratings[user]]
        user_bias = sum(user_bias) / len(user_bias)
        user_biases[user] = user_bias

    pass


if __name__ == "__main__":
    main(sys.argv)
