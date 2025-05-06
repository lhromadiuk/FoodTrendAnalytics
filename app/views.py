from flask import Blueprint, render_template, request, jsonify,current_app
from .search import search_recipes, get_es_client, ES_INDEX


from datetime import datetime, timedelta
import random
# Blueprint for main routes
bp = Blueprint('main', __name__)

@bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/search')
def search_page():
    query = request.args.get("q", "")
    if not query:
        return render_template("search.html", results=[], query="")

    results = search_recipes(query=query)
    return render_template("search.html", results=results, query=query)


@bp.route("/trends")
def ingredient_trend():
    ingredient = request.args.get("ingredient", "").lower()
    if not ingredient:
        return jsonify({"error": "Missing ingredient"}), 400

    # Simulate trend: past 6 months
    today = datetime.today()
    dates = [(today - timedelta(days=30 * i)).strftime("%Y-%m") for i in reversed(range(6))]
    counts = [random.randint(3, 15) for _ in dates]

    return jsonify({"dates": dates, "counts": counts})



@bp.route("/recipe/<id>")
def recipe_detail(id):
    es = get_es_client()
    try:
        res = es.get(index=ES_INDEX, id=id)
        r = res["_source"]
    except:
        return render_template("404.html"), 404

    return render_template("recipe.html", recipe=r)
