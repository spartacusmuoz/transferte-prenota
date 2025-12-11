"""rename hotel field to allogio

Revision ID: 7f964633c6e3
Revises: 96abc8960fe9
Create Date: 2025-12-08 07:48:26.751633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f964633c6e3'
down_revision: Union[str, None] = '96abc8960fe9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # rinomina la colonna hotel → alloggio
    op.alter_column(
        'hotel_api_params',
        'hotel',
        new_column_name='alloggio'
    )


def downgrade() -> None:
    # torna indietro: alloggio → hotel
    op.alter_column(
        'hotel_api_params',
        'alloggio',
        new_column_name='hotel'
    )
