"""merge heads

Revision ID: 4257f11bcb6e
Revises: 20251212_add_id_hotel, 84d1426072d6
Create Date: 2025-12-12 15:09:36.614165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4257f11bcb6e'
down_revision: Union[str, None] = ('20251212_add_id_hotel', '84d1426072d6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
