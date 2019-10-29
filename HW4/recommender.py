from collections import defaultdict
from math import sqrt
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


class Recommender(object):
    def __init__(self, ratings):
        self.user_ratings = defaultdict(lambda: defaultdict(float))
        self.movie_ratings = defaultdict(lambda: defaultdict(float))
        self.movie_biases = {}
        self.user_biases = {}

        for user, movie, rating in ratings:
            self.user_ratings[user][movie] = rating
            self.movie_ratings[movie][user] = rating

        self.global_mean = self.get_global_mean(ratings)


    def get_global_mean(self, ratings):
        total_ratings = []
        for user, movie, rating in ratings:
            total_ratings.append(rating)
        return sum(total_ratings) / len(total_ratings)


    def estimate_movie_biases(self):
        for movie in self.movie_ratings:
            # b_i = sum(r_ui - mu) / len(R(i))
            movie_bias = [rating - self.global_mean for rating in self.movie_ratings[movie].values()]
            movie_bias = sum(movie_bias) / len(movie_bias)
            self.movie_biases[movie] = movie_bias


    def estimate_user_biases(self):
        for user in self.user_ratings:
            # b_u = sum(r_ui - mu - b_i) / len(R(u))
            user_bias = [rating - self.global_mean - self.movie_biases[movie] for movie, rating in self.user_ratings[user].items()]
            user_bias = sum(user_bias) / len(user_bias)
            self.user_biases[user] = user_bias


    def pearson_correlation(self, movie1, movie2):
        intersect_users = set()
        for user in self.user_ratings:
            if movie1 in self.user_ratings[user] and movie2 in self.user_ratings[user]:
                intersect_users.add(user)
        
        # Set pearson correlation to 0 if there is no intersectional user
        if len(intersect_users) == 0:
            return 0.

        numerator = 0.
        denominator = 0.
        for user in intersect_users:
            numerator += (self.user_ratings[user][movie1] - self.baseline_predictor(user, movie1)) * (self.user_ratings[user][movie2] - self.baseline_predictor(user, movie2))
            denominator += (self.user_ratings[user][movie1] - self.baseline_predictor(user, movie1))**2 * (self.user_ratings[user][movie2] - self.baseline_predictor(user, movie2))**2
        
        return numerator / sqrt(denominator)


    def content_similarity(self, movie1, movie2):
        pass

        
    def baseline_predictor(self, user, movie):
        """Baseline predictor (b_ui)
        """
        return self.user_biases[user] + self.movie_biases[movie] + self.global_mean

    
    def predict(self, user, movie, similarity):
        bias = self.baseline_predictor(user, movie)

        numerator = 0.
        denominator = 0.
        for user_movie in self.user_ratings[user]:
            if similarity == 'pearson':
                numerator += self.pearson_correlation(movie, user_movie) * (self.user_ratings[user][user_movie] - self.baseline_predictor(user, user_movie))
                denominator += self.pearson_correlation(movie, user_movie)
            elif similarity == 'content':
                numerator += self.content_similarity(movie, user_movie) * (self.user_ratings[user][user_movie] - self.baseline_predictor(user, user_movie))
                denominator += self.content_similarity(movie, user_movie)
        
        return bias + numerator / denominator
    

def output_result(output, filename):
    with open(filename, 'w') as file:
        for row in output:
            file.write(row + '\n')


def main(argv):
    input_filename = 'HW4/input.txt'
    # input_filename = argv[1]
    # output_filename = argv[2]

    ratings, movies, queries = read_input(input_filename)
    
    recommender = Recommender(ratings)
    recommender.estimate_movie_biases()
    recommender.estimate_user_biases()
    
    v = recommender.predict(15, 7, 'pearson')
    print(v)
    pass


if __name__ == "__main__":
    main(sys.argv)
