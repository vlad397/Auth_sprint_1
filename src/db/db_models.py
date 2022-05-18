import uuid

from sqlalchemy.dialects.postgresql import UUID

from .db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    first_name = db.Column(db.String, unique=False, nullable=False)
    second_name = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=True)

    def __init__(self, first_name, second_name, email, login, password):
        self.first_name = first_name
        self.second_name = second_name
        self.email = email
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.login}>'
