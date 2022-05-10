import sqlalchemy
from .db_session import SqlAlchemyBase


class Clan(SqlAlchemyBase):
    __tablename__ = 'clan'

    role_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    id = sqlalchemy.Column(sqlalchemy.Integer)
    role_name = sqlalchemy.Column(sqlalchemy.String)