import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from werkzeug.security import check_password_hash, generate_password_hash

from auth.db.postgres import Base


class UserRole(Base):
    __tablename__ = 'user_roles'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('auth.roles.id'), primary_key=True)

    def __repr__(self):
        return f'<UserRole user_id={self.user_id}, role_id={self.role_id}>'


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    login = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship('Role', secondary='auth.user_roles', back_populates='users')
    login_history = relationship('LoginHistory', cascade='all, delete-orphan', backref='user', lazy='dynamic')


    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class Role(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    permissions = Column(ARRAY(String), nullable=True)

    users = relationship('User', secondary='auth.user_roles', back_populates='roles')

    def __init__(self, name: str, description: str = None, permissions: list = None):
        self.name = name
        self.description = description
        self.permissions = permissions if permissions else None

    def __repr__(self):
        return f'<Role {self.name}>'


class LoginHistory(Base):
    __tablename__ = 'login_history'
    __table_args__ = {'schema': 'auth'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete="CASCADE"), nullable=False)
    user_agent = Column(String(255), nullable=True)
    login_time = Column(DateTime, default=datetime.utcnow)

    Index('idx_login_history_user', 'user_id')

    def __init__(self, user_id: uuid.UUID, user_agent: str = None):
        self.user_id = user_id
        self.user_agent = user_agent

    def __repr__(self):
        return f'<LoginHistory user_id={self.user_id}>'
