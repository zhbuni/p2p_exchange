from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    surname = Column(String)
    telegram_id = Column(Integer)

    def __repr__(self):
        return "{} {}".format(self.name, self.surname)
