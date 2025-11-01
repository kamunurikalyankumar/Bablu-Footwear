import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/bablu_footwear'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'uploads')

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/bablu_footwear_test'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # MongoDB Atlas URI for production
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb+srv://admin:admin@mernapp.m9qyw.mongodb.net/bablu_footwear'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}