from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from .user import DeclarativeBase


class Payment(DeclarativeBase):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    russian_title = Column(String, nullable=False)
    english_title = Column(String, nullable=False)