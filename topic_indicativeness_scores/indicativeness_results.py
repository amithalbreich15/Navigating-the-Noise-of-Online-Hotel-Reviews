import csv
import os

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import pearsonr
import seaborn as sns

CLASSIFIED_DATA_FOLDER = os.path.join(os.pardir, 'data_topic_classified')
PLOTS_FOLDER_PATH = os.path.join(os.pardir, 'plots', 'topic_indicativeness_scores')
OUTPUT_RESULTS_PATH = os.path.join('results', 'result.csv')


def calculate_proportion_of_reviews(df: pd.DataFrame, topics: list[str]) -> dict[str, list[float]]:
    """
    Calculates the proportion of reviews discussing each topic.
    :param df: dataframe of hotel reviews.
    :param topics: list of reviews topics.
    :return: dictionary mapping between each topic and the proportion of reviews discussing it.
    """

    review_proportions = {topic: [] for topic in topics}
    total_reviews = df[["Positive Reviews", "Negative Reviews"]].notna().sum().sum()

    for topic in topics:
        pos_col = f"{topic} - positive"
        neg_col = f"{topic} - negative"
        topic_count = df[pos_col].sum() + df[neg_col].sum()

        if total_reviews > 0:
            proportion = topic_count / total_reviews
        else:
            proportion = 0

        review_proportions[topic].append(proportion)

    return review_proportions


def plot_review_proportions(review_proportions: dict[str, list[float]], topics: list[str]) -> None:
    """
    Plots the proportion of reviews discussing each topic individually.
    :param review_proportions: dictionary mapping between each topic and the proportion of reviews discussing it.
    :param topics: list of review topics.
    """

    review_proportions_df = pd.DataFrame(review_proportions)

    for i, topic in enumerate(topics):
        plt.hist(review_proportions_df[topic].dropna(), bins=20, color='lightcoral', edgecolor='black')
        bold_topic = r"$\mathbf{" + "}\ \mathbf{".join(topic.split()) + "}$"
        plt.title(f"Proportion of Reviews Discussing {bold_topic}")
        plt.xlabel("Proportion of Reviews")
        plt.ylabel("Number of Hotels")
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_FOLDER_PATH, f'review_topic_proportions_{topic}.png'))
        plt.show()


def calculate_sentiment_ratio(df: pd.DataFrame, topics: list[str]) -> dict[str, list[float]]:
    """
    Calculates the ratio between positive and negative reviews discussing each topic.
    :param df: dataframe of hotel reviews.
    :param topics: list of reviews topics.
    :return: dictionary mapping between each topic and the ratio between positive and negative reviews discussing it,
    where the ratio is mapped to range [-1, 1] such that -1 indicates only negative reviews;
     1 indicates only positive reviews; and 0 indicates an equal number of positive and negative reviews.
    """

    sentiment_ratios = {topic: [] for topic in topics}

    for topic in topics:
        pos_col = f"{topic} - positive"
        neg_col = f"{topic} - negative"
        pos_count = df[pos_col].sum()
        neg_count = df[neg_col].sum()

        if pos_count + neg_count > 0:
            ratio = (pos_count - neg_count) / (pos_count + neg_count)
        else:
            ratio = 0

        sentiment_ratios[topic].append(ratio)

    return sentiment_ratios


def plot_sentiment_ratios(sentiment_ratios: dict[str, list[float]], topics: list[str]) -> None:
    """
    Plots the ratio between positive and negative reviews discussing each topic.
    :param sentiment_ratios: dictionary mapping between each topic and the ratio between positive and negative reviews
     discussing it, where the ratio is mapped to range [-1, 1] such that -1 indicates only negative reviews;
     1 indicates only positive reviews; and 0 indicates an equal number of positive and negative reviews.
    :param topics: list of reviews topics.
    """

    sentiment_ratios_df = pd.DataFrame(sentiment_ratios)

    for i, topic in enumerate(topics):
        plt.hist(sentiment_ratios_df[topic].dropna(), bins=20, color='skyblue', edgecolor='black')
        bold_topic = r"$\mathbf{" + "}\ \mathbf{".join(topic.split()) + "}$"
        plt.title(f"Sentiment Ratio for {bold_topic}")
        plt.xlabel("Ratio (Positive - Negative)")
        plt.ylabel("Number of Hotels")
        plt.xlim(-1, 1)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_FOLDER_PATH, f'sentiment_ratios_{topic}.png'))
        plt.show()


def plot_sentiment_vs_rating_with_correlation(
        sentiment_ratios: dict[str, list[float]],
        overall_ratings: list[float],
        topics: list[str]
) -> None:

    for i, topic in enumerate(topics):
        sns.regplot(x=overall_ratings, y=sentiment_ratios[topic], scatter_kws={'alpha': 0.5})
        correlation, _ = pearsonr(sentiment_ratios[topic], overall_ratings)

        bold_topic = r"$\mathbf{" + "}\ \mathbf{".join(topic.split()) + "}$"
        plt.title(f"{bold_topic}\nCorrelation: {correlation:.2f}")

        plt.xlabel("Overall Rating")
        plt.ylabel("Sentiment Ratio (Positive - Negative)")
        plt.xlim(0, 10)
        plt.ylim(-1, 1)
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_FOLDER_PATH, f'sentiment_vs_rating_with_correlation_{topic}.png'))
        plt.show()


def save_sentiment_ratio_per_hotel(all_hotels_sentiment_ratios: dict[str, dict[str, list[float]]]) -> None:
    """
    Saves the sentiment ratio per hotel in an output .csv file.
    :param all_hotels_sentiment_ratios: dictionary mapping between each hotel name and the sentiment ratios
    of each topic.
    """

    with open(OUTPUT_RESULTS_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Hotel Name', 'Room amenities', 'Hotel amenities', 'Staff', 'Food and beverages', 'Location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for hotel_name, ratings in all_hotels_sentiment_ratios.items():
            row = {
                'Hotel Name': hotel_name,
                'Room amenities': ratings['Room amenities'][0],
                'Hotel amenities': ratings['Hotel amenities'][0],
                'Staff': ratings['Staff'][0],
                'Food and beverages': ratings['Food and beverages'][0],
                'Location': ratings['Location'][0]
            }
            writer.writerow(row)


if __name__ == "__main__":

    files = [os.path.join(CLASSIFIED_DATA_FOLDER, file) for file in os.listdir(CLASSIFIED_DATA_FOLDER) if file.endswith(".csv")]
    topics = ["Room amenities", "Hotel amenities", "Staff", "Food and beverages", "Location"]

    all_review_proportions = {topic: [] for topic in topics}
    all_sentiment_ratios = {topic: [] for topic in topics}
    overall_ratings = []

    all_hotels_sentiment_ratios = dict()
    for file_path in files:
        df = pd.read_csv(file_path)
        hotel_name = os.path.basename(file_path).replace("processed_reviews_", "").replace(".csv", "")

        review_proportions = calculate_proportion_of_reviews(df, topics)
        for topic in topics:
            all_review_proportions[topic].extend(review_proportions[topic])

        sentiment_ratios = calculate_sentiment_ratio(df, topics)
        all_hotels_sentiment_ratios[hotel_name] = sentiment_ratios
        for topic in topics:
            all_sentiment_ratios[topic].extend(sentiment_ratios[topic])

        overall_rating = df['Overall Average Rating'].mean()
        overall_ratings.append(overall_rating)

    plot_review_proportions(all_review_proportions, topics)
    plot_sentiment_ratios(all_sentiment_ratios, topics)
    plot_sentiment_vs_rating_with_correlation(all_sentiment_ratios, overall_ratings, topics)

    save_sentiment_ratio_per_hotel(all_hotels_sentiment_ratios)
