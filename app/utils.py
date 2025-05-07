from .embedding import tokenize_recipe, get_model, embed_tokens
from .models import Recipe

_recipe_vectors = None


def get_recipe_vectors():
    global _recipe_vectors
    if _recipe_vectors is None:
        print("Caching recipe vectors...")
        model = get_model()
        recipes = Recipe.query.all()
        _recipe_vectors = {
            r.id: embed_tokens(tokenize_recipe(r), model.wv)
            for r in recipes
        }
    return _recipe_vectors


def clear_recipe_vectors():
    global _recipe_vectors
    _recipe_vectors = None
