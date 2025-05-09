import re
import string

import nltk
import numpy as np
from nltk import WordNetLemmatizer, word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

_weights = {
    "cuisine": 3.2,
    "title": 2.7,
    "ingredients": 2.0,
    "instructions": 0
}


def embed_tokens(tokens, word_vectors):
    valid_tokens = [token for token in tokens if token in word_vectors.key_to_index]
    if not valid_tokens:
        return np.zeros(word_vectors.vector_size)
    return np.mean([word_vectors[token] for token in valid_tokens], axis=0)


def embed_weighted(tokenized_recipe, model):
    vectors = []
    total_weight = 0
    for section, tokens in tokenized_recipe.items():
        weight = _weights.get(section, 0)
        embedded_section = embed_tokens(tokens, model.wv)
        vectors.append(embedded_section * weight)
        total_weight += weight
    return np.sum(vectors, axis=0) / total_weight if total_weight > 0 else np.zeros(model.vector_size)


def tokenize_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return processed_tokens


def tokenize_recipe(recipe):
    return {
        "cuisine": tokenize_text(recipe.cuisine or ""),
        "title": tokenize_text(recipe.title or ""),
        "ingredients": tokenize_text(' '.join(i.name for i in recipe.ingredients)),
        "instructions": tokenize_text(recipe.instructions or "")
    }


def tokenize_recipe_flat(recipe):
    parts = [
        recipe.cuisine,
        recipe.title,
        ' '.join([ing.name for ing in recipe.ingredients]),
        recipe.instructions
    ]
    text = ' '.join([str(p) for p in parts if p])
    return tokenize_text(text)


""" train Word2Vec
def train_model(all_recipes, model_path="models/w2v.model"):
    tokenized_docs = [tokenize_recipe_flat(r) for r in all_recipes if r]

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
"""
