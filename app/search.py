# app/search.py
from elasticsearch import Elasticsearch
from flask import current_app

ES_INDEX = 'recipes'


def get_es_client():

    cfg = current_app.config
    endpoint = cfg.get('ELASTIC_ENDPOINT')
    api_key   = cfg.get('ELASTIC_API_KEY')

    if not endpoint or not api_key:
        raise RuntimeError("ENDPOINT and API_KEY must be set")

    return Elasticsearch(endpoint, api_key=api_key)


def init_index(es):

    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body={
            'mappings': {
                'properties': {
                    'title':        {'type': 'text'},
                    'cuisine':      {'type': 'keyword'},
                    'instructions': {'type': 'text'},
                    'ingredients':  {'type': 'keyword'},
                    'image_url': {'type': 'keyword'}
                }
            }
        })


def index_recipe(recipe):

    es = get_es_client()
    init_index(es)
    doc = {
        'title':        recipe.title,
        'cuisine':      recipe.cuisine,
        'instructions': recipe.instructions,
        'ingredients':  [ingredient.name.title() for ingredient in recipe.ingredients]
    }
    es.index(index=ES_INDEX, id=recipe.id, document=doc)


def search_recipes(query, cuisine=None, ingredient=None):
    es = get_es_client()
    init_index(es)

    body = {
        'query': {
            'bool': {
                'must': {
                    'multi_match': {
                        'query': query,
                        'fields': ['title', 'instructions']
                    }
                }
            }
        }
    }
    if cuisine:
        body['query']['bool'].setdefault('filter', []).append({'term': {'cuisine': cuisine}})
    if ingredient:
        body['query']['bool'].setdefault('filter', []).append({'term': {'ingredients': ingredient}})

    res = es.search(index=ES_INDEX, body=body)
    return [
        {
            "id": hit["_id"],
            "title": hit["_source"]["title"],
            "cuisine": hit["_source"]["cuisine"],
            "score": hit["_score"]
        }
        for hit in res["hits"]["hits"]
    ]
