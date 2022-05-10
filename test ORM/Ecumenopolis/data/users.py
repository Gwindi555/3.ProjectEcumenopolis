import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    name = sqlalchemy.Column(sqlalchemy.String)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    cash = sqlalchemy.Column(sqlalchemy.Integer)
    rep = sqlalchemy.Column(sqlalchemy.Integer)
    lvl = sqlalchemy.Column(sqlalchemy.Integer)
    server_id = sqlalchemy.Column(sqlalchemy.Integer)
