import os

import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
from wordcloud import WordCloud

DATA_FOLDER_PATH = os.path.join(os.pardir, 'data')
PLOTS_FOLDER_PATH = os.path.join(os.pardir, 'plots', 'topic_indicativeness_scores')


def preprocess_text(review_text: str) -> str:
    """
    Preprocess the given reviews to remove stop words.
    :param review_text: one positive or negative review from hotel reviews dataframe.
    :return: Preprocessed review.
    """

    stop_words = set(stopwords.words('english'))
    words = word_tokenize(review_text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return " ".join(filtered_words)


def generate_word_cloud(positive_text: str, negative_text: str) -> None:
    """
    Generates word clouds for the positive and negative reviews.
    :param positive_text: one string containing all preprocessed positive reviews, without stop-words.
    :param negative_text:  one string containing all preprocessed negative reviews, without stop-words.
    """

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Negative Reviews Word Cloud
    wordcloud_neg = WordCloud(width=800, height=400, background_color='white').generate(negative_text)
    axes[0].imshow(wordcloud_neg, interpolation='bilinear')
    axes[0].set_title("Negative Reviews Word Cloud", fontsize=20)
    axes[0].axis('off')

    # Positive Reviews Word Cloud
    wordcloud_pos = WordCloud(width=800, height=400, background_color='white').generate(positive_text)
    axes[1].imshow(wordcloud_pos, interpolation='bilinear')
    axes[1].set_title("Positive Reviews Word Cloud", fontsize=20)
    axes[1].axis('off')
    plt.tight_layout()

    plt.savefig(os.path.join(PLOTS_FOLDER_PATH, 'reviews_word_clouds.png'))
    plt.show()


if __name__ == "__main__":
    positive_reviews = []
    negative_reviews = []

    for file in os.listdir(DATA_FOLDER_PATH):
        if file.endswith('.csv'):
            file_path = os.path.join(DATA_FOLDER_PATH, file)
            hotel_reviews_df = pd.read_csv(file_path)

            positive_reviews.extend(hotel_reviews_df['Positive Reviews'].dropna().apply(preprocess_text))
            negative_reviews.extend(hotel_reviews_df['Negative Reviews'].dropna().apply(preprocess_text))

    positive_text = " ".join(positive_reviews)
    negative_text = " ".join(negative_reviews)

    # Plot word clouds.
    generate_word_cloud(positive_text, negative_text)
