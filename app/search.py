from numpy import dot
from numpy.linalg import norm

from app.embedding import tokenize_text, embed_weighted
from app.models import Recipe
from app.utils import get_recipe_vectors, get_model, get_cuisines, get_ingredients


def cosine_similarity(vec1, vec2):
    denominator = norm(vec1) * norm(vec2)
    return dot(vec1, vec2) / denominator if denominator != 0 else 0


def tokenize_query(query):
    tokens = tokenize_text(query)
    cuisine_set = get_cuisines()
    ingredient_set = get_ingredients()

    categorized = {
        "cuisine": [],
        "title": [],
        "ingredients": [],
        "instructions": []
    }

    for word in tokens:
        if word in cuisine_set:
            categorized["cuisine"].append(word)
        elif word in ingredient_set:
            categorized["ingredients"].append(word)
        else:
            categorized["title"].append(word)

    return categorized


def search_recipes(query):  # semantic search using Word2Vec
    model = get_model()
    q_vec = embed_weighted(tokenize_query(query), model)
    recipes_vectors = get_recipe_vectors()
    scores = []
    for rid, vec in recipes_vectors.items():
        sim = cosine_similarity(q_vec, vec)
        scores.append((rid, sim))

    top_matches = sorted(scores, key=lambda x: x[1], reverse=True)[:10]

    recipes = Recipe.get_by_ids([rid for rid, _ in top_matches])
    recipe_dict = {r.id: r for r in recipes}

    return [
        {
            "title": recipe_dict[rid].title,
            "score": round(sim * 100, 2),
            "cuisine": recipe_dict[rid].cuisine,
            "id": rid
        }
        for rid, sim in top_matches
        if rid in recipe_dict
    ]
