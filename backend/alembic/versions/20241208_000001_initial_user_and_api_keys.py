"""Initial user and api_keys tables

Revision ID: 001_initial
Revises:
Create Date: 2024-12-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('customer', 'agent', 'admin', 'api_service', name='userrole'),
                  default='customer', nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', 'pending_verification', name='userstatus'),
                  default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('api_key_hash', sa.String(255), nullable=True),
    )

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('scopes', sa.String(500), default=''),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Integer(), default=1),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('api_keys')
    op.drop_table('users')

    # Drop enums (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS userstatus')
