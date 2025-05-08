import string

import click
import requests
from flask import current_app
from flask.cli import with_appcontext

from .database import db
from .elastic_search import index_recipe
from .models import Recipe, Ingredient
from .utils import reload_model


def ingest_data():
    """fetch recipes from API and store + index them for elastic search"""
    base_url = current_app.config['MEALDB_URL']
    total_added = 0
    for letter in string.ascii_lowercase:
        url = f"{base_url}{letter}"

        meals = requests.get(url).json().get('meals') or []
        for item in meals:
            rid = int(item['idMeal'])
            if not Recipe.query.get(rid):
                r = Recipe(
                    id=rid,
                    title=item['strMeal'],
                    cuisine=item['strArea'],
                    instructions=item.get('strInstructions', ''),
                    published_at=item.get('dateModified', ''),
                    image_url=item.get('strMealThumb', '')
                )
                db.session.add(r)
                for i in range(1, 21):
                    name = item.get(f'strIngredient{i}')  # .title()
                    if name and name.strip():
                        name = name.strip().lower()
                        ing = Ingredient.query.filter_by(name=name).first() or Ingredient(name=name)
                        db.session.add(ing)
                        if ing not in r.ingredients:
                            r.ingredients.append(ing)
                db.session.commit()
                index_recipe(r)
                total_added += 1
    return total_added


@click.command('ingest-data')
@with_appcontext
def cli_ingest_data():
    total_added = ingest_data()
    click.echo(f'Ingestion complete, {total_added} recipes added')
    reload_model()


@click.command('train-word2vec')
@with_appcontext
def cli_train_word2vec():
    from .embedding import train_model
    from .models import Recipe
    all_recipes = Recipe.query.all()

    train_model(all_recipes)
