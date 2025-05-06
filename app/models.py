from .database import db

# Association table for many-to-many Recipe ⇄ Ingredient
recipe_ingredients = db.Table(
    'recipe_ingredients',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
)

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    cuisine = db.Column(db.String, index=True)
    instructions = db.Column(db.Text)
    published_at = db.Column(db.Date)
    image_url = db.Column(db.String)
    ingredients = db.relationship(
        'Ingredient', secondary=recipe_ingredients, back_populates='recipes'
    )

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, index=True)
    recipes = db.relationship(
        'Recipe', secondary=recipe_ingredients, back_populates='ingredients'
    )