import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Elasticsearch
    ELASTIC_ENDPOINT = os.getenv('ELASTIC_ENDPOINT', '')
    ELASTIC_API_KEY = os.getenv('ELASTIC_API_KEY', '')
    INGEST_TOKEN = os.getenv('INGEST_TOKEN', '')
    # Data ingestion
    MEALDB_URL = os.getenv('MEALDB_URL', '')

    # Word2Vec m
    W2V_MODEL_PATH = os.getenv('W2V_MODEL_PATH', 'models/w2v.model')
