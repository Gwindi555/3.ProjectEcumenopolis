import sqlalchemy
from .db_session import SqlAlchemyBase


class Shop(SqlAlchemyBase):
    __tablename__ = 'shop'

    role_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    id = sqlalchemy.Column(sqlalchemy.Integer)
    cost = sqlalchemy.Column(sqlalchemy.Integer)
