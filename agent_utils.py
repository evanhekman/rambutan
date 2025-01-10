import os
import sqlite3
import json
import math
import re
import datetime
from collections import Counter


def initialize_agent(agent_name, agent_root_prompt):
    """This function creates a folder for the agent based on the name and initializes
    the prompt file, tweet database, and creates the other necessary files."""
    os.makedirs(agent_name, exist_ok=True)

    prompt_path = os.path.join(agent_name, "prompt.txt")
    with open(prompt_path, "w") as f:
        f.write(agent_root_prompt)

    config_path = os.path.join(agent_name, "config.json")
    config_data = {"agent_name": agent_name, "last_updated": None, "post_count": 0}
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)

    create_tweet_db(agent_name)


def create_tweet_db(agent_name):
    """This function initializes the tweet database for the agent."""
    db_path = os.path.join(agent_name, "tweets.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """
    )

    conn.commit()
    conn.close()


def add_tweet_to_db(agent_name, tweet):
    """This function adds a tweet to the agent's tweet database and timestamps it."""
    db_path = os.path.join(agent_name, "tweets.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO tweets (text, timestamp) VALUES (?, ?)", (tweet, timestamp)
    )

    conn.commit()
    conn.close()


def get_last_n_tweets(agent_name, n):
    """This function retrieves the last n tweets from the agent's tweet database."""
    db_path = os.path.join(agent_name, "tweets.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT text FROM tweets ORDER BY id DESC LIMIT ?", (n,))
    tweets = cursor.fetchall()

    conn.close()
    return [tweet[0] for tweet in tweets]


def calculate_tfidf(agent_name):
    """Calculate TF-IDF scores for all tweets in the database"""
    # Get tweets from database
    database_path = os.path.join(agent_name, "tweets.db")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM tweets ORDER BY timestamp DESC LIMIT 500")
    tweets = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Tokenize tweets
    tokenized_tweets = [tweet.split() for tweet in tweets]

    # Calculate TF
    tf_list = []
    for tokens in tokenized_tweets:
        term_count = Counter(tokens)
        total_terms = len(tokens)
        tf = {term: count / total_terms for term, count in term_count.items()}
        tf_list.append(tf)

    # Calculate IDF
    df = Counter()
    for tokens in tokenized_tweets:
        unique_terms = set(tokens)
        for term in unique_terms:
            df[term] += 1

    total_docs = len(tweets)
    idf = {term: math.log(total_docs / (1 + freq)) for term, freq in df.items()}

    # Calculate TF-IDF
    tfidf_list = []
    for tf in tf_list:
        tfidf = {term: tf[term] * idf[term] for term in tf}
        tfidf_list.append(tfidf)

    return tfidf_list


def compute_similarity(vec1, vec2):
    """Compute cosine similarity between two TF-IDF vectors"""
    common_terms = set(vec1.keys()) & set(vec2.keys())

    dot_product = sum(vec1[term] * vec2[term] for term in common_terms)

    magnitude1 = math.sqrt(sum(value**2 for value in vec1.values()))
    magnitude2 = math.sqrt(sum(value**2 for value in vec2.values()))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def tweet_similarity(new_tweet, agent_name):
    """Calculate similarity between new tweet and existing tweets"""
    # Get existing tweets from database
    database_path = os.path.join(agent_name, "tweets.db")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM tweets ORDER BY timestamp DESC LIMIT 500")
    existing_tweets = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Add new tweet and calculate TF-IDF for all
    all_tweets = existing_tweets + [new_tweet]
    tfidf_vectors = calculate_tfidf(agent_name)

    # Compare new tweet vector with all existing
    new_vector = tfidf_vectors[-1]
    similarities = [compute_similarity(new_vector, vec) for vec in tfidf_vectors[:-1]]

    return max(similarities) if similarities else 0.0
