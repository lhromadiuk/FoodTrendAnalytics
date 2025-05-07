import os
import re
import string

import numpy as np
from flask import current_app
from gensim.models import Word2Vec
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from app.models import Recipe

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def get_model():
    model_path = current_app.config.get('W2V_MODEL_PATH')
    if not model_path:
        return train_model(Recipe.query.all())
    return Word2Vec.load(model_path)


def embed_tokens(tokens, word_vectors):
    valid_tokens = [token for token in tokens if token in word_vectors.key_to_index]
    if not valid_tokens:
        return np.zeros(word_vectors.vector_size)
    return np.mean([word_vectors[token] for token in valid_tokens], axis=0)


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return processed_tokens


def tokenize_recipe(recipe):
    tokens = [
        recipe.cuisine,
        recipe.title,
        ' '.join([ing.name for ing in recipe.ingredients]),
        recipe.instructions
    ]
    text = ' '.join(tokens)
    return preprocess_text(text)


def train_model(all_recipes, model_path="models/w2v.model"):
    tokenized_docs = [tokenize_recipe(r) for r in all_recipes if r]

    model = Word2Vec(
        sentences=tokenized_docs,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4
    )

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"Word2Vec model trained and saved to {model_path}")
    return model
