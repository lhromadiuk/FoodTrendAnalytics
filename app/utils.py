import os
from types import SimpleNamespace

from gensim.downloader import load
from gensim.models import KeyedVectors

from .embedding import tokenize_recipe, embed_weighted, tokenize_recipe_flat, embed_tokens
from .models import Recipe, Ingredient

_recipe_vectors = None
_model = None
_cuisines = None
_ingredients = None
_spell_checker = None
_recipes = None


def get_model():
    global _model
    path = "models/glove_100.kv"
    if _model:
        return _model

    if os.path.exists(path):
        print("Loading GloVe model from local file...")
        kv = KeyedVectors.load(path, mmap='r')
    else:
        print("Downloading GloVe model...")
        kv = load("glove-wiki-gigaword-100")
        kv.save(path)
    _model = SimpleNamespace(wv=kv, vector_size=kv.vector_size)
    return _model


def get_spellchecker():
    global _spell_checker
    if _spell_checker is None:
        from spellchecker import SpellChecker
        _spell_checker = SpellChecker()
        domain_words = build_domain_vocabulary(get_recipes())
        _spell_checker.word_frequency.load_words(domain_words)
        print(f"Spellchecker loaded with {len(domain_words)} domain-specific words.")
    return _spell_checker


def get_recipes():
    global _recipes
    if _recipes is None:
        _recipes = set(Recipe.query.all())
    return _recipes


def build_domain_vocabulary(recipes):
    words = set()
    for recipe in recipes:
        words.update(recipe.title.lower().split())
        words.update(recipe.cuisine.lower())
        for ing in recipe.ingredients:
            words.update(ing.name.lower().split())

        if recipe.instructions:
            words.update(recipe.instructions.lower().split())
    return {w.strip(".,()") for sub in words for w in (sub if isinstance(sub, list) else [sub])}


def get_recipe_vectors():
    global _recipe_vectors
    if _recipe_vectors is None:
        print("Caching recipe vectors...")
        model = get_model()
        recipes = Recipe.query.all()
        global _recipes
        _recipes = recipes
        _recipe_vectors = {
            r.id: 0.6 * embed_weighted(tokenize_recipe(r), model) + 0.4 * embed_tokens(tokenize_recipe_flat(r),
                                                                                       model.wv)
            for r in recipes
        }
    return _recipe_vectors


def get_cuisines():
    global _cuisines
    if _cuisines is None:
        _cuisines = set({c[0].lower() for c in Recipe.query.with_entities(Recipe.cuisine).distinct() if c[0]})
    return _cuisines


def get_ingredients():
    global _ingredients
    if _ingredients is None:
        _ingredients = set({i.name.lower() for i in Ingredient.query.all() if i.name})
    return _ingredients


def reload_model():
    global _model
    _model = None
    clear_recipe_vectors()
    reload_cuisines()
    reload_ingredients()


def reload_ingredients():
    global _ingredients
    _ingredients = None


def reload_cuisines():
    global _cuisines
    _cuisines = None


def clear_recipe_vectors():
    global _recipe_vectors
    _recipe_vectors = None
