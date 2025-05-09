from types import SimpleNamespace

import numpy as np
import pytest

from app.embedding import (
    tokenize_text,
    tokenize_recipe,
    tokenize_recipe_flat,
    embed_tokens,
    embed_weighted
)


@pytest.fixture
def test_soup_recipe():
    return SimpleNamespace(
        cuisine="italian",
        title="chicken soup",
        ingredients=[SimpleNamespace(name="chicken"), SimpleNamespace(name="salt")],
        instructions="boil it slowly"
    )


@pytest.fixture
def empty_recipe():
    return SimpleNamespace(
        cuisine=None,
        title=" ",
        ingredients=[],
        instructions=None
    )


@pytest.fixture
def word_vectors():
    class TestW2V:
        def __init__(self):
            self.vector_size = 4
            self.key_to_index = {"chicken": 0, "soup": 1, "boil": 2, "italian": 3}
            self.vectors = {
                "chicken": np.array([1, 0, 0, 0]),
                "soup": np.array([0, 1, 0, 0]),
                "boil": np.array([0, 0, 1, 0]),
                "italian": np.array([0, 0, 0, 1]),
            }

        def __getitem__(self, key):
            return self.vectors[key]

    return TestW2V()


@pytest.fixture
def test_model(word_vectors):
    return SimpleNamespace(wv=word_vectors, vector_size=4)


def test_tokenize_text_removes_stopwords():
    tokens = tokenize_text("The chicken soup .")
    assert "chicken" in tokens
    assert "the" not in tokens


def test_tokenize_recipe_structure(test_soup_recipe):
    tokenized = tokenize_recipe(test_soup_recipe)
    assert isinstance(tokenized, dict)
    assert all(k in tokenized for k in ["cuisine", "title", "ingredients", "instructions"])
    assert "chicken" in tokenized["title"]
    assert "italian" in tokenized["cuisine"]


def test_tokenize_recipe_flat(test_soup_recipe):
    tokens = tokenize_recipe_flat(test_soup_recipe)
    assert isinstance(tokens, list)
    assert "chicken" in tokens
    assert "boil" in tokens


def test_embed_tokens_known_words(word_vectors):
    tokens = ["chicken", "soup"]
    vec = embed_tokens(tokens, word_vectors)
    expected = np.mean([
        word_vectors["chicken"],
        word_vectors["soup"]
    ], axis=0)
    assert np.allclose(vec, expected)


def test_embed_tokens_all_unknown(word_vectors):
    vec = embed_tokens(["error", "unknown"], word_vectors)
    assert np.allclose(vec, np.zeros(word_vectors.vector_size))


def test_embed_weighted_vector_shape(test_soup_recipe, test_model):
    tokenized = tokenize_recipe(test_soup_recipe)
    vec = embed_weighted(tokenized, test_model)
    assert vec.shape == (4,)


def test_embed_weighted_handles_empty_fields(empty_recipe, test_model):
    tokenized = tokenize_recipe(empty_recipe)
    vec = embed_weighted(tokenized, test_model)
    assert np.allclose(vec, np.zeros(test_model.vector_size))


def test_embed_weighted_correct_weights_math(test_model):
    test_soup_recipe = SimpleNamespace(
        cuisine="italian",
        title="chicken soup",
        ingredients=[SimpleNamespace(name="chicken")],
        instructions="boil soup"
    )
    tokenized = tokenize_recipe(test_soup_recipe)
    vec = embed_weighted(tokenized, test_model)

    # Expected weighted vector :
    # cuisine: [0,0,0,1]*1.8
    # title: avg([1,0,0,0], [0,1,0,0]) -> [0.5, 0.5, 0, 0] * 2.0
    # ingredients: [1,0,0,0] * 1.5
    # instructions: avg([0,0,1,0], [0,1,0,0]) -> [0, 0.5, 0.5, 0] * 0

    expected = (
                       3.2 * np.array([0, 0, 0, 1]) +
                       2.7 * np.array([0.5, 0.5, 0, 0]) +
                       2.0 * np.array([1, 0, 0, 0]) +
                       0 * np.array([0, 0.5, 0.5, 0])
               ) / (3.2 + 2.7 + 2.0 + 0)

    assert np.allclose(vec, expected)
