import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Elasticsearch
    ELASTIC_ENDPOINT = os.getenv('ELASTIC_ENDPOINT','')
    ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY', '')

    # Data ingestion
    MEALDB_URL = os.getenv('MEALDB_URL', 'https://www.themealdb.com/api/json/v1/1/search.php?f=a')