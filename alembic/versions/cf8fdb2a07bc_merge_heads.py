"""Merge heads

Revision ID: cf8fdb2a07bc
Revises: 9901c6360da7, 2025xxxx
Create Date: 2025-12-15 16:16:21.362778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf8fdb2a07bc'
down_revision: Union[str, None] = ('9901c6360da7', '2025xxxx')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
