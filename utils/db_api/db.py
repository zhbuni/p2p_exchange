from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models.user import DeclarativeBase
from dotenv import load_dotenv
import os


class Database:
    def __init__(self):
        load_dotenv()
        user = os.environ.get("DB_USER")
        port = os.environ.get("DB_PORT")
        password = os.environ.get("DB_PASSWORD")
        name = os.environ.get("DB_NAME")
        host = os.environ.get("DB_HOST")
        engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}')
        DeclarativeBase.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()