from collections import Counter

import tensorflow as tf
import numpy as np

from preprocessing import NLP_Preprocessor

COEFFICIENT = 3


def process_comments(text_data, pos_keywords, neg_keywords):
    # Seed
    np.random.seed(4)
    tf.random.set_seed(4)

    # Text preprocessing
    nlp_preprocessor = NLP_Preprocessor()

    prep_text_data = nlp_preprocessor.split_sent(text_data)
    tokens = nlp_preprocessor.tokenize(prep_text_data)
    tokens = nlp_preprocessor.lowercase(tokens)
    tokens = nlp_preprocessor.lemmatize_tokens(tokens)
    tokens = nlp_preprocessor.remove_stopwords(tokens)
    tokens = nlp_preprocessor.remove_punctuation(tokens)
    prep_text_data = nlp_preprocessor.tokens_to_text(tokens)

    # Sentiment analysis
    nn_sentiment = nlp_preprocessor.get_sentiments(prep_text_data)

    # Keywords analysis

    def analyze_keywords(text_data):
        pos_keywords_counter = Counter()
        neg_keywords_counter = Counter()
        keywords_sentiment = []

        for comment in text_data:
            words = comment.split()
            num_words = len(words)
            sentiment = 0

            for word in words:
                if word in pos_keywords:
                    sentiment += 1 / num_words
                    pos_keywords_counter[word] += 1
                elif word in neg_keywords:
                    sentiment -= 1 / num_words
                    neg_keywords_counter[word] += 1
            keywords_sentiment.append(sentiment)
        return np.array(keywords_sentiment), (pos_keywords_counter, neg_keywords_counter)

    keywords_sentiment, (pos_keywords_counter, neg_keywords_counter) = analyze_keywords(text_data)

    compound_sentiment = nn_sentiment + keywords_sentiment * COEFFICIENT
    pos_comments = np.array(text_data)[compound_sentiment > 0]
    neg_comments = np.array(text_data)[compound_sentiment < 0]
    num_pos_sentiment = (compound_sentiment > 0).sum()
    num_neg_sentiment = (compound_sentiment < 0).sum()

    return compound_sentiment.mean(), num_pos_sentiment, num_neg_sentiment, pos_keywords_counter, neg_keywords_counter
