# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # External APIs
    API_KEY = os.environ.get('API_KEY')
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://sipa.ingr.in')
    
    # Render specific
    PORT = int(os.environ.get('PORT', 10000))
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
