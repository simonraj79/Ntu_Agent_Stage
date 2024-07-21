import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    @staticmethod
    def get_database_url():
        url = os.environ.get('DATABASE_URL')
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')

    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 60,
        'pool_pre_ping': True,
    }
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables")

    @classmethod
    def log_config(cls):
        print("Configuration loaded:")
        print(f"Using {'production' if os.environ.get('FLASK_ENV') == 'production' else 'development'} environment")
        print(f"Database: {'PostgreSQL' if cls.SQLALCHEMY_DATABASE_URI.startswith('postgresql://') else 'SQLite'}")
        print(f"OpenAI API Key: {'Set' if cls.OPENAI_API_KEY else 'Not set'}")

    @staticmethod
    def get_base_url():
        return os.environ.get('BASE_URL') or ''