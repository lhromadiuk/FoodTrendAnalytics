import click
import requests
from flask import current_app
from flask.cli import with_appcontext
from .database import db
from .models import Recipe, Ingredient
from .search import index_recipe

@click.command('ingest-data')
@with_appcontext
def ingest_data():
    """Fetch recipes from API and store + index them"""
    url = current_app.config['MEALDB_URL']
    meals = requests.get(url).json().get('meals') or []
    for item in meals:
        rid = int(item['idMeal'])
        if not Recipe.query.get(rid):
            r = Recipe(
                id=rid,
                title=item['strMeal'],
                cuisine=item['strArea'],
                instructions=item.get('strInstructions',''),
                image = item.get('strMealThumb','')
            )
            db.session.add(r)
            for i in range(1, 21):
                name = item.get(f'strIngredient{i}')
                if name:
                    ing = Ingredient.query.filter_by(name=name).first() or Ingredient(name=name)
                    db.session.add(ing)
                    r.ingredients.append(ing)
            db.session.commit()
            index_recipe(r)
    click.echo('Ingestion complete')