import click
import requests
from flask import current_app
from flask.cli import with_appcontext
from .database import db
from .models import Recipe, Ingredient
from .search import index_recipe
import string



def ingest_data():
    """Fetch recipes from API and store + index them"""
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
                    instructions=item.get('strInstructions',''),
                    image_url = item.get('strMealThumb','')
                )
                db.session.add(r)
                for i in range(1, 21):
                    name = item.get(f'strIngredient{i}')  #.title()
                    if name:
                        ing = Ingredient.query.filter_by(name=name).first() or Ingredient(name=name)
                        db.session.add(ing)
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