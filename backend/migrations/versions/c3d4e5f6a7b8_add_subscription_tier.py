"""Add subscription tier to users

Revision ID: c3d4e5f6a7b8
Revises: b1e2f3a4c5d6
Create Date: 2026-02-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b1e2f3a4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('subscription_tier', sa.String(), nullable=False, server_default='free'))
    op.add_column('users', sa.Column('subscription_updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'subscription_updated_at')
    op.drop_column('users', 'subscription_tier')
