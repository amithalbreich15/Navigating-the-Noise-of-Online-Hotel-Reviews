import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PAGERANK_REVIEWS_SCORES_FOLDER = 'pagerank_results'
TOPICS = ['Room amenities', 'Hotel amenities', 'Staff', 'Food and beverages', 'Location']
PAGERANK_PLOTS_FOLDER = os.path.join(os.pardir, 'plots', 'pagerank_reviews')


def load_pagerank_results() -> list[pd.DataFrame]:
    """
    Loads PageRank results.
    :return: A list of dataframes, where each dataframe is a topic-classified hotel reviews dataframe,
    in which the reviews are sorted according to their PageRank score.
    """

    results = []

    for file_name in os.listdir(PAGERANK_REVIEWS_SCORES_FOLDER):
        if file_name.endswith('.csv'):
            file_path = os.path.join(PAGERANK_REVIEWS_SCORES_FOLDER, file_name)
            pagerank_scored_hotel_reviews_df = pd.read_csv(file_path)
            results.append(pagerank_scored_hotel_reviews_df)

    return results


def calculate_differences(
        pagerank_scored_hotel_reviews_dfs: list[pd.DataFrame],
        num_random_iterations: int = 100
) -> tuple[dict[str, list[float]], dict[str, list[float]]]:
    """
    Calculates the difference, in absolute value, between the indicativeness results of a hotel calculated over the
    entire reviews dataframe - and those calculated over two subsets of the reviews:
    - the 10 top-scored reviews (by the PageRank scores)
    - A random subset of 10 reviews
    :param pagerank_scored_hotel_reviews_dfs: A list of dataframes, where each dataframe is a topic-classified
    hotel reviews dataframe, in which the reviews are sorted according to their PageRank score.
    :param num_random_iterations: number of iterations of sampling random 10 reviews and calculating the indicativeness
    results with respect to this subset of reviews.
    :return: mapping between each topic, and the differences between indicativeness results calculated in both methods.
    """

    differences_top_10 = {topic: [] for topic in TOPICS}
    differences_random_10 = {topic: [] for topic in TOPICS}

    for df in pagerank_scored_hotel_reviews_dfs:
        indicativeness_scores = calculate_indicativeness_scores(df)

        # Indicativeness scores based on top 10 PageRank reviews.
        top_10_reviews = df.head(10)
        indicativeness_scores_based_on_top_scored_reviews = calculate_indicativeness_scores(top_10_reviews)

        for topic in TOPICS:
            difference = abs(indicativeness_scores[topic] - indicativeness_scores_based_on_top_scored_reviews[topic])
            differences_top_10[topic].append(difference)

        # Indicativeness scores based on a random subset of 10 reviews (averaged over multiple iterations).
        for _ in range(num_random_iterations):
            random_10_reviews = df.sample(10)
            indicativeness_scores_based_on_random_reviews = calculate_indicativeness_scores(random_10_reviews)

            for topic in TOPICS:
                difference = abs(indicativeness_scores[topic] - indicativeness_scores_based_on_random_reviews[topic])
                differences_random_10[topic].append(difference)

    return differences_top_10, differences_random_10


def calculate_indicativeness_scores(reviews_subset: pd.DataFrame) -> dict[str, float]:
    """
    Calculates the indicativeness scores based on the given subset of reviews.
    :param reviews_subset: subset of hotel reivews.
    :return: indicativeness score of each topic.
    """

    sentiment_ratios = {}

    for topic in TOPICS:
        positive_reviews_col = reviews_subset[f'{topic} - positive']
        num_positive_reviews_for_topic = positive_reviews_col.sum()

        negative_reviews_col = reviews_subset[f'{topic} - negative']
        num_negative_reviews_for_topic = negative_reviews_col.sum()

        num_reviews_for_topic = len(reviews_subset[(positive_reviews_col == 1) | (negative_reviews_col == 1)])

        if num_reviews_for_topic > 0:
            score = (num_positive_reviews_for_topic - num_negative_reviews_for_topic) / num_reviews_for_topic
        else:
            score = 0

        sentiment_ratios[topic] = score

    return sentiment_ratios


def plot_differences(differences_top_10: dict[str, list[float]], differences_random_10: dict[str, list[float]]) -> None:
    """
    Plots the average estimation error of the indicativeness scores.
    :param differences_top_10: differences, in absolute value, between the indicativeness results of topics calculated
     over the entire reviews dataframe - and those calculated over the 10 top-scored reviews (by the PageRank scores).
    :param differences_random_10: differences, in absolute value, between the indicativeness results of topics
     calculated over the entire reviews dataframe - and those calculated over random subsets of 10 reviews.
    """

    average_difference_calculated_based_on_top_10 = []
    errors_of_calculations_based_on_top_10 = []

    average_difference_calculated_based_on_random_10 = []
    errors_of_calculations_based_on_random_10 = []

    for topic in TOPICS:
        average_diff_for_topic = np.mean(differences_top_10[topic])
        std_diff_for_topic = np.std(differences_top_10[topic])
        average_difference_calculated_based_on_top_10.append(average_diff_for_topic)
        errors_of_calculations_based_on_top_10.append(std_diff_for_topic)

        average_diff_for_topic = np.mean(differences_random_10[topic])
        std_diff_for_topic = np.std(differences_random_10[topic])
        average_difference_calculated_based_on_random_10.append(average_diff_for_topic)
        errors_of_calculations_based_on_random_10.append(std_diff_for_topic)

    x = np.arange(len(TOPICS))
    width = 0.35

    plt.figure(figsize=(10, 6))

    plt.bar(x - width / 2, average_difference_calculated_based_on_top_10, width, yerr=errors_of_calculations_based_on_top_10, capsize=5, label='Top 10 PageRank scored Reviews',
            color='skyblue')
    plt.bar(x + width / 2, average_difference_calculated_based_on_random_10, width, yerr=errors_of_calculations_based_on_random_10, capsize=5, label='Random 10 Reviews',
            color='lightgreen')

    # plt.xlabel('Topic')
    plt.ylabel('Average Difference')
    plt.title('Estimation Error of Topic Indicativeness Scores')
    plt.xticks(x, TOPICS)
    plt.legend()
    plt.tight_layout()

    plt.savefig(os.path.join(PAGERANK_PLOTS_FOLDER, 'estimation_error_of_topic_indicativeness_scores.png'))
    plt.show()


if __name__ == '__main__':
    pagerank_scored_hotel_reviews_df: list[pd.DataFrame] = load_pagerank_results()
    differences_top_10, differences_random_10 = calculate_differences(pagerank_scored_hotel_reviews_df)
    plot_differences(differences_top_10, differences_random_10)
