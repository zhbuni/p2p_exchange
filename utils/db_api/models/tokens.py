from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from .user import DeclarativeBase


class Token(DeclarativeBase):
    __tablename__ = 'token'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_type = Column(String, nullable=False)