import os
from dotenv import load_dotenv


load_dotenv()


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY', 'devkey')
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'library.db')}")
SQLALCHEMY_TRACK_MODIFICATIONS = False