import os

class Config:
    SECRET_KEY = "your_secret_key_here"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"  # Use SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
