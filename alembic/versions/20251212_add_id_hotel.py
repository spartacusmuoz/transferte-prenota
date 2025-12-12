"""Aggiunta colonna id_hotel a prenotazioni

Revision ID: 20251212_add_id_hotel
Revises: 14d189c655b4
Create Date: 2025-12-12 14:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251212_add_id_hotel'
down_revision: Union[str, None] = '14d189c655b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Aggiungi la colonna 'id_hotel'
    op.add_column('prenotazioni', sa.Column('id_hotel', sa.Integer(), nullable=True))

    # Se vuoi aggiungere FK (opzionale)
    # op.create_foreign_key(
    #     'fk_prenotazioni_hotel',
    #     'prenotazioni',
    #     'hotel_suggeriti',
    #     ['id_hotel'],
    #     ['id']
    # )

def downgrade() -> None:
    # Rimuovi la colonna in caso di rollback
    op.drop_column('prenotazioni', 'id_hotel')
