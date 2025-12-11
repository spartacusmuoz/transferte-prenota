"""add hotel and exists_in_db to hotel_api_params

Revision ID: 96abc8960fe9
Revises: b8daa293fb2e
Create Date: 2025-12-07 19:44:03.819560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96abc8960fe9'
down_revision: Union[str, None] = 'b8daa293fb2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # aggiunge le colonne senza cancellare i dati esistenti
    op.add_column('hotel_api_params', sa.Column('hotel', sa.String(), nullable=True))
    op.add_column('hotel_api_params', sa.Column('exists_in_db', sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade():
    op.drop_column('hotel_api_params', 'hotel')
    op.drop_column('hotel_api_params', 'exists_in_db')

