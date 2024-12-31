import matplotlib.pyplot as plt
import os
import pandas as pd


def calculate_statistics(folder_path: str) -> dict[str, float]:
    """
    Calculates the statistics of data files from the given path.
    :param folder_path: path to data files folder.
    :return: dictionary with statistic of the datafiles.
    """

    total_houses = 0
    total_reviews = 0
    max_reviews = 0
    min_reviews = float('inf')
    total_ratings = 0
    max_rating = 0
    min_rating = float('inf')
    total_file_size = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)

            total_houses += 1

            # Filter out rows where both 'Negative Reviews' and 'Positive Reviews' are empty
            non_empty_reviews_df = df.dropna(subset=['Negative Reviews', 'Positive Reviews'], how='all')
            num_reviews = len(non_empty_reviews_df)

            total_reviews += num_reviews
            max_reviews = max(max_reviews, num_reviews)
            min_reviews = min(min_reviews, num_reviews)

            avg_rating = df['Overall Average Rating'].mean()
            total_ratings += avg_rating
            max_rating = max(max_rating, avg_rating)
            min_rating = min(min_rating, avg_rating)

            # Calculate file size in KB
            file_size_kb = os.path.getsize(file_path) / 1024.0
            total_file_size += file_size_kb

    avg_reviews_per_house = total_reviews / total_houses if total_houses > 0 else 0
    avg_overall_rating = total_ratings / total_houses if total_houses > 0 else 0
    avg_file_size_per_house = total_file_size / total_houses if total_houses > 0 else 0

    return {
        'Number of houses scraped': total_houses,
        'Average reviews per house': avg_reviews_per_house,
        'Max reviews per house': max_reviews,
        'Min reviews per house': min_reviews,
        'Average overall rating per house': avg_overall_rating,
        'Max overall rating per house': max_rating,
        'Min overall rating per house': min_rating,
        'Average file size per house (in KB)': avg_file_size_per_house
    }


def plot_overall_rating_histogram(overall_ratings) -> None:
    """
    Plots histogram of the overall rating of accommodations.
    """

    plt.figure(figsize=(8, 6))
    plt.hist(overall_ratings, bins=10, edgecolor='black')
    plt.title('Histogram of Overall Ratings of Houses')
    plt.xlabel('Overall Rating')
    plt.ylabel('Number of Accommodations')
    plt.show()


if __name__ == "__main__":
    folder_path = 'data'

    # Print statistics of data files.
    stats = calculate_statistics(folder_path)
    for key, value in stats.items():
        print(f"{key}: {value:.2f}")

    # Plot histogram of the overall average rating of accommodations .
    overall_ratings = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            avg_rating = df['Overall Average Rating'].mean()
            overall_ratings.append(avg_rating)

    plot_overall_rating_histogram(overall_ratings)
