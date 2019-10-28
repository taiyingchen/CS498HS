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


if __name__ == "__main__":
    main(sys.argv)
