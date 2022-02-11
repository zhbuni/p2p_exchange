from sqlalchemy import Column, Integer, String
from .user import DeclarativeBase


class Currency(DeclarativeBase):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
