import os

class Config:
    SECRET_KEY = 'dev'  # Change this in production
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://reqsense_user:reqsense_pass@localhost:5432/reqsense'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
