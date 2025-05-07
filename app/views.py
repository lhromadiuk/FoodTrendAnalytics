import random
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, jsonify, current_app, abort

from .ingest import ingest_data
from .models import Recipe
from .search import search_recipes

bp = Blueprint('main', __name__)


@bp.route('/')
def dashboard():
    return render_template('dashboard.html')


@bp.route('/search')
def search_page():
    query = request.args.get("q", "")
    if not query:
        return render_template("search.html", results=[], query="")

    results = search_recipes(query)

    return render_template("search.html", results=results, query=query)


@bp.route("/trends")
def ingredient_trend():
    ingredient = request.args.get("ingredient", "").strip().lower()
    if not ingredient:
        return jsonify({"error": "Missing ingredient"}), 400

    # Simulate trend: past 6 months
    today = datetime.today()
    dates = [(today - timedelta(days=30 * i)).strftime("%Y-%m") for i in reversed(range(6))]
    counts = [random.randint(3, 15) for _ in dates]

    return jsonify({"dates": dates, "counts": counts})


@bp.route("/run-ingest")
def run_ingest():
    token = request.args.get("token")
    if token != current_app.config.get("INGEST_TOKEN"):
        abort(403)
    try:
        with current_app.app_context():
            total_added = ingest_data()
        return f" Ingestion triggered, {total_added} recipes added"
    except Exception as e:
        print(f" Ingestion failed: {e}")
        return render_template("404.html"), 404


@bp.route("/recipe/<id>")
def recipe_detail(id):
    recipe = Recipe.get_by_id(id)
    if not recipe:
        return render_template("404.html"), 404

    return render_template("recipe.html", recipe=recipe)
