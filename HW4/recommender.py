import sys
from collections import defaultdict
from math import log, sqrt

import numpy as np


class Recommender(object):
    """
    Object for recommend movies to users using item-item neighborhood models

    Parameters
    ----------
    ratings : list
        List of rating records
        Each element is a tuple of (user_id, movie_id, rating_score)
    """

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
        """Return the average of all the ratings
        """
        total_ratings = []
        for user, movie, rating in ratings:
            total_ratings.append(rating)
        return sum(total_ratings) / len(total_ratings)

    def estimate_movie_biases(self):
        """Estimate movie biases (b_i)
        """
        for movie in self.movie_ratings:
            # b_i = sum(r_ui - mu) / len(R(i))
            movie_bias = [rating - self.global_mean for rating in self.movie_ratings[movie].values()]
            movie_bias = sum(movie_bias) / len(movie_bias)
            self.movie_biases[movie] = movie_bias

    def estimate_user_biases(self):
        """Estimate user bias (b_u)
        """
        for user in self.user_ratings:
            # b_u = sum(r_ui - mu - b_i) / len(R(u))
            user_bias = [rating - self.global_mean - self.movie_biases[movie]
                         for movie, rating in self.user_ratings[user].items()]
            user_bias = sum(user_bias) / len(user_bias)
            self.user_biases[user] = user_bias

    def pearson_correlation(self, movie1, movie2):
        """Return movie-movie similarity using Pearson correlation
        """
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
            numerator += (self.user_ratings[user][movie1] - self.baseline_predictor(user, movie1)) * (
                self.user_ratings[user][movie2] - self.baseline_predictor(user, movie2))
            denominator += (self.user_ratings[user][movie1] - self.baseline_predictor(user, movie1))**2 * (
                self.user_ratings[user][movie2] - self.baseline_predictor(user, movie2))**2

        return numerator / sqrt(denominator)

    def compute_tfidf(self, movies):
        """Compute TF (term frequency) and IDF (inverse document frequency)
        """
        term2index = {}  # {term: index}
        term2doc_cnt = defaultdict(int)  # {term: document count}
        num_terms = 0
        for movie in movies:
            term_set = set()
            terms = movies[movie].split()
            for term in terms:
                if term not in term_set:
                    term2doc_cnt[term] += 1
                    term_set.add(term)

                if term not in term2index:
                    term2index[term] = num_terms
                    num_terms += 1

        self.tf = {}  # {movie_id: tf}
        for movie in movies:
            self.tf[movie] = np.zeros(num_terms)
            terms = movies[movie].split()
            for term in terms:
                self.tf[movie][term2index[term]] += 1

        self.idf = np.zeros(num_terms)
        for term in term2doc_cnt:
            self.idf[term2index[term]] = log(len(movies) / term2doc_cnt[term])

    def get_tfidf(self, movie):
        """Return TF-IDF vector of the given movie
        """
        return self.tf[movie] * self.idf

    def cosine_similarity(self, x, y):
        """Return consine similarity between two vectors
        """
        return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

    def content_similarity(self, movie1, movie2):
        """Return content similarity using cosine similarity between two TF-IDF vectors
        """
        v1, v2 = self.get_tfidf(movie1), self.get_tfidf(movie2)
        return self.cosine_similarity(v1, v2)

    def baseline_predictor(self, user, movie):
        """Baseline predictor (b_ui)
        b_ui = b_u + b_i + mu
        """
        return self.user_biases[user] + self.movie_biases[movie] + self.global_mean

    def predict(self, user, movie, similarity):
        """Predict rating using movie-movie similarity
        
        Parameters
        ----------
        user : int
            User id
        movie : int
            Movie id
        similarity : string
            Specify 'pearson' to use pearson correlation
            Specify 'content' to use content similarity
        """
        bias = self.baseline_predictor(user, movie)

        numerator = 0.
        denominator = 0.
        for user_movie in self.user_ratings[user]:
            if similarity == 'pearson':
                numerator += self.pearson_correlation(movie, user_movie) * (
                    self.user_ratings[user][user_movie] - self.baseline_predictor(user, user_movie))
                denominator += self.pearson_correlation(movie, user_movie)
            elif similarity == 'content':
                numerator += self.content_similarity(movie, user_movie) * (
                    self.user_ratings[user][user_movie] - self.baseline_predictor(user, user_movie))
                denominator += self.content_similarity(movie, user_movie)

        return bias + numerator / denominator


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


def main(argv):
    input_filename = argv[1]
    output_filename = argv[2]

    ratings, movies, queries = read_input(input_filename)

    recommender = Recommender(ratings)
    recommender.estimate_movie_biases()
    recommender.estimate_user_biases()
    recommender.compute_tfidf(movies)

    with open(output_filename, 'w') as file:
        for user, movie in queries:
            rating_pearson = recommender.predict(user, movie, 'pearson')
            rating_content = recommender.predict(user, movie, 'content')
            rating_pearson = round(rating_pearson, 1)
            rating_content = round(rating_content, 1)

            print(f'===== user: {user}, movie: {movie} =====')
            print(f'rating with pearson correlation: {rating_pearson}')
            print(f'rating with content similarity: {rating_content}')

            print(f'user: {user}, movie: {movie}', file=file)
            print(f'rating with pearson correlation: {rating_pearson}', file=file)
            print(f'rating with content similarity: {rating_content}', file=file)


if __name__ == "__main__":
    main(sys.argv)
