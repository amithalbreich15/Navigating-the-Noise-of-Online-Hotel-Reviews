import os

import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import normalize

TOPIC_CLASSIFIED_DATA_FOLDER = os.path.join(os.pardir, 'data_topic_classified')
PAGERANK_REVIEWS_SCORES_FOLDER = 'pagerank_results'
TOPICS_COLUMNS = [
    'Room amenities - positive', 'Room amenities - negative',
    'Hotel amenities - positive', 'Hotel amenities - negative',
    'Staff - positive', 'Staff - negative',
    'Food and beverages - positive', 'Food and beverages - negative',
    'Location - positive', 'Location - negative'
]
PAGERANK_SCORE_COLUMN_NAME = 'PageRank Score'


def extract_topic_sentiment_vectors_for_single_hotel(hotel_reviews_df: pd.DataFrame) -> np.ndarray:
    """
    Extracts the (topic, sentiment) vectors for the reviews of the given hotel.
    :param hotel_reviews_df: Topic-classified reviews data file of a single hotel.
    :return: Normalised (topic, sentiment) matrix with vector for the reviews.
    """

    topic_sentiment_matrix = hotel_reviews_df[TOPICS_COLUMNS].values
    normalized_matrix = normalize(topic_sentiment_matrix, norm='l2')
    return normalized_matrix


def build_reviews_graph(reviews_similarity_matrix: np.ndarray) -> nx.Graph:
    """
    Builds a reviews graph using the similarity matrix between reviews:
     - each node represents a user review as a whole (both the positive and negative comments).
     - Edges are added between any two nodes that share at least one common (topic, sentiment) pair.
     - The weight of each edge is determined by the similarity matrix.
    :param reviews_similarity_matrix: Similarity matrix between reviews, calculated as the normalised dot product
      between the (topic, sentiment) vectors of the two nodes.
    :return: The initialized graph.
    """

    G = nx.Graph()
    num_reviews = reviews_similarity_matrix.shape[0]
    G.add_nodes_from(range(num_reviews))

    for i in range(num_reviews):
        for j in range(i + 1, num_reviews):
            if reviews_similarity_matrix[i, j] > 0:  # Only add edges with positive similarity
                G.add_edge(i, j, weight=reviews_similarity_matrix[i, j])

    return G


def save_scores(hotel_reviews_df: pd.DataFrame, pagerank_scores: dict[int, float], output_file_path: str) -> None:
    """
    Saves a dataframe of the reviews sorted by the PageRank scores, with an additional column with the scores.
    :param hotel_reviews_df: Topic-classified reviews data file of a single hotel.
    :param pagerank_scores:
    :param output_file_path: path of output file.
    """

    hotel_reviews_df[PAGERANK_SCORE_COLUMN_NAME] = hotel_reviews_df.index.map(pagerank_scores)
    df_sorted = hotel_reviews_df.sort_values(by=PAGERANK_SCORE_COLUMN_NAME, ascending=False)
    df_sorted.to_csv(output_file_path, index=False)
    print(f"Saved sorted PageRank results to {output_file_path}")


if __name__ == '__main__':
    if not os.path.exists(PAGERANK_REVIEWS_SCORES_FOLDER):
        os.makedirs(PAGERANK_REVIEWS_SCORES_FOLDER)

    for file_name in os.listdir(TOPIC_CLASSIFIED_DATA_FOLDER):
        if file_name.endswith('.csv'):
            file_path = os.path.join(TOPIC_CLASSIFIED_DATA_FOLDER, file_name)
            hotel_reviews_df = pd.read_csv(file_path)

            # Extract (topic, sentiment) vectors for this hotel.
            normalized_topic_matrix = extract_topic_sentiment_vectors_for_single_hotel(hotel_reviews_df)

            # Calculate the similarity between reviews (weights for the edges in the graph) using these vectors.
            similarity_matrix = (1 - squareform(pdist(normalized_topic_matrix, 'cosine')))

            # Initialize the graph and run the PageRank algorithm.
            G = build_reviews_graph(similarity_matrix)
            pagerank_scores = nx.pagerank(G, weight='weight')

            # Save PageRank results to output folder.
            output_file_path = os.path.join(PAGERANK_REVIEWS_SCORES_FOLDER, f"pagerank_{file_name}")
            save_scores(hotel_reviews_df, pagerank_scores, output_file_path)
