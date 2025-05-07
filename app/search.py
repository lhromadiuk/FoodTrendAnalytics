from numpy import dot
from numpy.linalg import norm

from app.embedding import preprocess_text, get_model, embed_tokens
from app.models import Recipe
from app.utils import get_recipe_vectors


def cosine_similarity(vec1, vec2):
    denominator = norm(vec1) * norm(vec2)
    return dot(vec1, vec2) / denominator if denominator != 0 else 0


def search_recipes(query):  # semantic search using Word2Vec
    model = get_model()
    q_vec = embed_tokens(preprocess_text(query), model.wv)
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
