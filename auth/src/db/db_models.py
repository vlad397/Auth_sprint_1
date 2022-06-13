from datetime import datetime
import enum
import uuid
from sqlalchemy import UniqueConstraint

from sqlalchemy.dialects.postgresql import UUID

from .db import db


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "users_sign_in" FOR VALUES IN ('web')"""
    )


class BasicRoleEnum(enum.Enum):
    admin = 'admin'
    superadmin = 'superadmin'

    @classmethod
    def list(cls):
        return list(map(lambda r: r.value, cls))


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, unique=False, nullable=False)

    def __str__(self):
        return self.name

    class Meta:
        PROTECTED_ROLE_NAMES = [
            BasicRoleEnum.admin.value,
            BasicRoleEnum.superadmin.value,
        ]


class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )

    id = db.Column(db.BigInteger(), primary_key=True)
    user_id = db.Column(
        "user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    role_id = db.Column(
        "role_id", UUID(as_uuid=True), db.ForeignKey("roles.id"))

    def __str__(self):
        return f"<User {self.user_id}> Role {self.role_id}"


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    first_name = db.Column(db.String, unique=False, nullable=False)
    second_name = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    roles = db.relationship(
        "Role",
        secondary="roles_users",
        backref=db.backref("users", lazy="dynamic"),
    )
    social_networks = db.relationship(
        "SocialNetwork",
        secondary="social_user",
        backref=db.backref("users", lazy="dynamic"),
    )

    def __init__(self, first_name, second_name, email, login, password):
        self.first_name = first_name
        self.second_name = second_name
        self.email = email
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.login}>'

    def roles_list(self) -> list[str]:
        return [role.name for role in self.roles]

    def social_list(self) -> list[str]:
        return [social.name for social in self.social_networks]


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blocklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class AuthHistory(db.Model):
    __tablename__ = "auth_history"
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    user_id = db.Column(
        "user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    timestamp = db.Column(db.DateTime)
    browser = db.Column(db.Text, nullable=True)
    platform = db.Column(db.Text, nullable=True)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f'{self.timestamp}::{self.browser}::{self.platform}'


class SocialNetwork(db.Model):
    __tablename__ = "social"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                   unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)

    def __str__(self):
        return self.name


class SocialUser(db.Model):
    __tablename__ = "social_user"
    __table_args__ = (
        db.UniqueConstraint('user_id', 'social_id', name='unique_user_social'),
    )

    id = db.Column(db.BigInteger(), primary_key=True)
    user_id = db.Column(
        "user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    social_id = db.Column(
        "social_id", UUID(as_uuid=True), db.ForeignKey("social.id"))

    def __str__(self):
        return f"<User {self.user_id} Network {self.social_id}>"
