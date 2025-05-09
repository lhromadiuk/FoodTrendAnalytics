from numpy import dot
from numpy.linalg import norm

from app.embedding import tokenize_text, embed_weighted, embed_tokens
from app.models import Recipe
from app.utils import get_recipe_vectors, get_model, get_cuisines, get_ingredients, get_spellchecker


def cosine_similarity(vec1, vec2):
    denominator = norm(vec1) * norm(vec2)
    return dot(vec1, vec2) / denominator if denominator != 0 else 0


def tokenize_query(query):
    tokens = tokenize_text(query)
    cuisine_set = get_cuisines()
    ingredient_set = get_ingredients()
    spell_checker = get_spellchecker()
    print(ingredient_set)
    print(cuisine_set)
    categorized = {
        "cuisine": [],
        "title": [],
        "ingredients": [],
        "instructions": []
    }

    corrected_tokens = [spell_checker.correction(t) if t not in spell_checker.word_frequency else t
                        for t in tokens]

    for word in corrected_tokens:
        if word in cuisine_set:
            categorized["cuisine"].append(word)
        elif word in ingredient_set:
            categorized["ingredients"].append(word)
        else:
            categorized["title"].append(word)

    return categorized


def get_score_for_id(scores, target_id):
    for rid, sim in scores:
        if rid == target_id:
            return sim
    return None


def search_recipes(query):
    model = get_model()
    q_vec_categorized = embed_weighted(tokenize_query(query), model)
    q_vec_flat = embed_tokens(tokenize_text(query), model.wv)
    recipes_vectors = get_recipe_vectors()
    q_vec = 0.4 * q_vec_categorized + 0.6 * q_vec_flat
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
