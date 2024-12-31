import os
import re
import string

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn import decomposition
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_FOLDER_PATH = PAGERANK_PLOTS_FOLDER = os.path.join(os.pardir, 'data')
PLOTS_FOLDER_PATH = os.path.join(os.pardir, 'plots', 'topic_indicativeness_scores')


def preprocess_reviews(folder_path: str) -> list[str]:
    """
    Reads hotel reviews from the given path and pre-process the text.
    :param folder_path: path to folder of hotel data files.
    :return: positive & negative hotel reviews, tokenized into sentences, with stop words removed and words lemmatized.
    """

    reviews = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            positive_reviews = df['Positive Reviews'].dropna().tolist()
            negative_reviews = df['Negative Reviews'].dropna().tolist()
            reviews.extend(positive_reviews)
            reviews.extend(negative_reviews)

    # Tokenization to sentences.
    sent_tokenized_reviews = [sentence for review in reviews for sentence in sent_tokenize(review)]

    # Clean text.
    cleaned_reviews = [clean_text(review) for review in sent_tokenized_reviews]

    # Remove stop words
    cleaned_reviews_without_stop_words = [remove_stop_words(review) for review in cleaned_reviews]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(w) for w in cleaned_reviews_without_stop_words]
    return lemmatized_tokens


def clean_text(sentence: str) -> str:
    """
    Removes punctuations from the given text sentence and converts it to lowercase.
    :param sentence: text sentence from hotel reviews.
    :return: cleaned sentence.
    """

    sentence = sentence.lower()
    sentence = re.sub(f'[{re.escape(string.punctuation)}]', '', sentence)
    return sentence


def remove_stop_words(sentence: str) -> str:
    """
    Removes stop word from the given sentence.
    :param sentence: cleaned text sentence from hotel reviews.
    :return: sentence, with stop words removed
    """

    stop_words = set(stopwords.words('english'))
    sentence = sentence.split()
    sentence = [w for w in sentence if not w.lower() in stop_words]
    sentence = " ".join(sentence)
    return sentence


def dimensionality_reduction(tokens: list[str], n_components=2) -> tuple[list[tuple[str, float]], list[list[float]]]:
    """
    Encodes each word from the reviews using its TF-IDF scores with respect to all review sentences.
    The function then applies Singular Value Decomposition (SVD) to reduce the dimensionality of
    the TF-IDF matrix, which helps in identifying the most significant features.
    :param tokens: list of sentence-tokenized, pre-processed hotel reviews.
    :param n_components: lumber of components for SVD dimensionality reduction.
    :return: list of tuples containing words and their corresponding TF-IDF scores sorted in descending order;
    and the reduced-dimensionality SVD matrix of shape (num_sentences x n_components).
    """

    tfv = TfidfVectorizer(tokenizer=word_tokenize, token_pattern=None)
    corpus_transformed = tfv.fit_transform(tokens)

    svd = decomposition.TruncatedSVD(n_components=n_components)
    corpus_svd = svd.fit_transform(corpus_transformed)
    feature_scores = dict(
        zip(
            tfv.get_feature_names_out(),
            svd.components_[0]
        )
    )

    sorted_feature_scores = sorted(feature_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_feature_scores, corpus_svd


def plot_top_scored_nouns(sorted_feature_scores: list[tuple[str, float]], top_n: int) -> None:
    """
    Plots the top-scoring nouns and their corresponding scores on a logarithmic scale.
    :param sorted_feature_scores: A sorted list of tuples where each tuple contains a word (str),
     and its corresponding score (float).
    :param top_n: number of top-scored words to plot.
    """

    # Filter only nouns from the sorted feature scores.
    noun_scores = [
        (word, score) for word, score in sorted_feature_scores
        if pos_tag([word])[0][1] in ['NN', 'NNS', 'NNP', 'NNPS']
    ]

    top_noun_scores = noun_scores[:top_n]
    topics = [item[0] for item in top_noun_scores]
    scores = [item[1] for item in top_noun_scores]

    plt.plot(range(1, top_n + 1), np.log(scores), marker='o')
    plt.title(f'Top-scored {top_n} Nouns (Log Scale)')
    plt.xlabel('Noun Rank')
    plt.ylabel('Log(Score)')
    plt.xticks(range(1, top_n + 1), topics, rotation=45, ha="right", fontsize=10)
    plt.tight_layout()

    plt.savefig(os.path.join(PLOTS_FOLDER_PATH, 'extract_topics_tfidf_top_nouns_scores_log_scale.png'))
    plt.show()


if __name__ == '__main__':
    lemmatized_tokens: list[str] = preprocess_reviews(DATA_FOLDER_PATH)
    sorted_feature_scores, corpus_svd = dimensionality_reduction(lemmatized_tokens)

    plot_top_scored_nouns(sorted_feature_scores, top_n=25)
