"""merge heads

Revision ID: 9901c6360da7
Revises: 4257f11bcb6e, xxxx
Create Date: 2025-12-14 09:20:29.951579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9901c6360da7'
down_revision: Union[str, None] = ('4257f11bcb6e', 'xxxx')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
