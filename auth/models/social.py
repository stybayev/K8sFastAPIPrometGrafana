from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship, backref
import uuid
from auth.db.postgres import Base
from auth.models.users import User


class SocialAccount(Base):
    __tablename__ = 'social_account'
    __table_args__ = (
        UniqueConstraint('social_id', 'social_name', name='social_pk'),
        {"schema": "auth"}
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=False)
    user = relationship(User, backref=backref('social_accounts', lazy=True))

    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
