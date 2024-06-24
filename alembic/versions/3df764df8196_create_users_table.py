from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '3df764df8196'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create schema if not exists
    op.execute('CREATE SCHEMA IF NOT EXISTS auth')

    bind = op.get_bind()

    # Check if 'roles' table exists
    if not bind.dialect.has_table(bind, 'roles', schema='auth'):
        op.create_table('roles',
                        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
                        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
                        sa.Column('description', sa.String(length=255), nullable=True),
                        sa.Column('permissions', sa.ARRAY(sa.String()), nullable=True),
                        sa.PrimaryKeyConstraint('id'),
                        sa.UniqueConstraint('name'),
                        schema='auth'
                        )

    # Check if 'users' table exists
    if not bind.dialect.has_table(bind, 'users', schema='auth'):
        op.create_table('users',
                        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
                        sa.Column('login', sa.String(length=255), nullable=False, unique=True),
                        sa.Column('password', sa.String(length=255), nullable=False),
                        sa.Column('first_name', sa.String(length=50), nullable=True),
                        sa.Column('last_name', sa.String(length=50), nullable=True),
                        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
                        sa.PrimaryKeyConstraint('id'),
                        sa.UniqueConstraint('login'),
                        schema='auth'
                        )

    # Check if 'login_history' table exists
    if not bind.dialect.has_table(bind, 'login_history', schema='auth'):
        op.create_table('login_history',
                        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
                        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id'), nullable=False),
                        sa.Column('user_agent', sa.String(length=255), nullable=True),
                        sa.Column('login_time', sa.DateTime(), default=sa.func.now()),
                        sa.UniqueConstraint('id'),
                        schema='auth'
                        )

    # Check if 'user_roles' table exists
    if not bind.dialect.has_table(bind, 'user_roles', schema='auth'):
        op.create_table('user_roles',
                        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
                        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id'), nullable=False),
                        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('auth.roles.id'), nullable=False),
                        sa.UniqueConstraint('id'),
                        schema='auth'
                        )


def downgrade() -> None:
    op.drop_table('user_roles', schema='auth')
    op.drop_table('login_history', schema='auth')
    op.drop_table('users', schema='auth')
    op.drop_table('roles', schema='auth')
    op.execute('DROP SCHEMA IF EXISTS auth CASCADE')
