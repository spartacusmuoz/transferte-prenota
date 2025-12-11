"""Merge heads

Revision ID: 147a3c7ad4cb
Revises: 14c721b89e16, xxxx_add_hotel_key_to_hotel_suggeriti
Create Date: 2025-12-03 13:01:26.693399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '147a3c7ad4cb'
down_revision: Union[str, None] = ('14c721b89e16', 'xxxx_add_hotel_key_to_hotel_suggeriti')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
