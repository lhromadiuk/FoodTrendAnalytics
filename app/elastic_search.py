from elasticsearch import Elasticsearch
from flask import current_app

ES_INDEX = 'recipes'


def get_es_client():
    cfg = current_app.config
    endpoint = cfg.get('ELASTIC_ENDPOINT')
    api_key = cfg.get('ELASTIC_API_KEY')

    if not endpoint or not api_key:
        raise RuntimeError("ENDPOINT and API_KEY must be set")

    return Elasticsearch(endpoint, api_key=api_key)


def init_index(es):
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body={
            'mappings': {
                'properties': {
                    'title': {
                        'type': 'text'
                    },
                    'cuisine': {
                        'type': 'text',
                        'fields': {
                            'raw': {'type': 'keyword'}
                        }
                    },
                    'instructions': {
                        'type': 'text'
                    },
                    'ingredients': {
                        'type': 'text',
                        'fields': {
                            'raw': {'type': 'keyword'}
                        }
                    },
                    'image_url': {
                        'type': 'keyword'
                    }
                }
            }

        })


def index_recipe(recipe):
    es = get_es_client()
    init_index(es)
    doc = {
        'title': recipe.title,
        'cuisine': recipe.cuisine,
        'instructions': recipe.instructions,
        'ingredients': [ingredient.name for ingredient in recipe.ingredients],
        'image_url': recipe.image_url
    }
    es.index(index=ES_INDEX, id=recipe.id, document=doc)


def search_recipes_elastic(query):  # search using elasticsearch
    query = query.strip().lower()
    es = get_es_client()
    init_index(es)

    body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "title": {
                                "query": query,
                                "boost": 8
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "ingredients": {
                                "query": query,
                                "boost": 6
                            }
                        }
                    },
                    {
                        "match": {
                            "title": {
                                "query": query,
                                "boost": 5,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "match": {
                            "ingredients": {
                                "query": query,
                                "boost": 4,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "match": {
                            "instructions": {
                                "query": query,
                                "boost": 3
                            }
                        }
                    },
                    {
                        "match": {
                            "cuisine": {
                                "query": query,
                                "boost": 5,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "ingredients": {
                                            "query": query,
                                            "fuzziness": "AUTO"
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "cuisine": {
                                            "query": query,
                                            "fuzziness": "AUTO"
                                        }
                                    }
                                }, {
                                    "match": {
                                        "instructions": {
                                            "query": query,
                                            "fuzziness": "AUTO"
                                        }
                                    }
                                }

                            ],
                            "boost": 5
                        }
                    }
                ]
            }}}

    res = es.search(index=ES_INDEX, body=body)
    return [
        {
            "id": hit["_id"],
            "title": hit["_source"]["title"],
            "cuisine": hit["_source"]["cuisine"],
            "image_url": hit["_source"].get("image_url"),
            "score": hit["_score"]
        }
        for hit in res["hits"]["hits"]
    ]
