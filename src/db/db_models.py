import enum
import uuid

from sqlalchemy.dialects.postgresql import UUID

from .db import db


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
        return f"<Role {self.name}>"

    class Meta:
        PROTECTED_ROLE_NAMES = (
            BasicRoleEnum.admin.value,
            BasicRoleEnum.superadmin.value,
        )


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

    def __init__(self, first_name, second_name, email, login, password, role):
        self.first_name = first_name
        self.second_name = second_name
        self.email = email
        self.login = login
        self.password = password
        self.role = role

    def __repr__(self):
        return f'<User {self.login}>'

    def roles_list(self) -> list[str]:
        return [role.name for role in self.roles]


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