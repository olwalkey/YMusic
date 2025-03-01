"""2.0.7 migrations

Revision ID: 1043e22bf2d1
Revises: 5f9d796c38b5
Create Date: 2024-09-30 14:36:06.820184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1043e22bf2d1'
down_revision: Union[str, None] = '5f9d796c38b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('playlists', 'requests')


def downgrade() -> None:
    op.rename_table('requests', 'playlists')
