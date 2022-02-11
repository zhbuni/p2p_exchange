from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from .user import DeclarativeBase, User


class Proposal(DeclarativeBase):
    __tablename__ = 'proposal'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_type = Column(Integer, ForeignKey('token.id'))
    price = Column(Float, nullable=False)
    min_amount = Column(Float, nullable=False)
    max_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    proposal_type = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    info = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    token = relationship('Token')
    user = relationship(User)