from tokenize import Name
from unicodedata import name
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from db.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    first_name = Column(String, unique=False, nullable=False)
    second_name = Column(String, unique=False, nullable=False)
    email = Column(String, unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __init__(self, first_name, second_name, email, login, password):
        self.first_name = first_name
        self.second_name = second_name
        self.email = email
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.login}>'