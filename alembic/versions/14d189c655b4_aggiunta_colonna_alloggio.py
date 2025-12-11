"""Aggiunta colonna alloggio

Revision ID: 14d189c655b4
Revises: d11675f340ff
Create Date: 2025-12-08 13:16:46.218557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14d189c655b4'
down_revision: Union[str, None] = 'd11675f340ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Aggiungi la colonna 'alloggio' alla tabella 'hotel_api_params' (se non esiste)
    #op.add_column('hotel_api_params', sa.Column('alloggio', sa.String(), nullable=True))
    
    # Rimuovi la colonna 'allogio' dalla tabella 'hotel_api_params' (se esiste)
    op.drop_column('hotel_api_params', 'allogio')

def downgrade() -> None:
    # In caso di rollback, rimuovi la colonna 'alloggio' e ripristina 'allogio'
    op.drop_column('hotel_api_params', 'alloggio')
    #op.add_column('hotel_api_params', sa.Column('allogio', sa.String(), nullable=True))

