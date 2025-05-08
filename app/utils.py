from flask import current_app
from gensim.models import Word2Vec

from .embedding import tokenize_recipe, embed_weighted, train_model, tokenize_recipe_flat, embed_tokens
from .models import Recipe, Ingredient

_recipe_vectors = None
_model = None
_cuisines = None
_ingredients = None
_spell_checker = None


def get_model():
    global _model
    if _model is None:
        model_path = current_app.config.get('W2V_MODEL_PATH')
        if not model_path:
            return train_model(Recipe.query.all())
        _model = Word2Vec.load(model_path)
    return _model


def get_spellchecker():
    global _spell_checker
    if _spell_checker is None:
        from spellchecker import SpellChecker
        _spell_checker = SpellChecker()
    return _spell_checker


def get_recipe_vectors():
    global _recipe_vectors
    if _recipe_vectors is None:
        print("Caching recipe vectors...")
        model = get_model()
        recipes = Recipe.query.all()
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
