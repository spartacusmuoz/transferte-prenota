"""Crea hotel_suggeriti e aggiungi citta/indirizzo a prenotazioni

Revision ID: 14c721b89e16
Revises: c106ec18dbaa
Create Date: 2025-12-01 11:33:28.320773
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '14c721b89e16'
down_revision: Union[str, None] = 'c106ec18dbaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Creazione tabella hotel_suggeriti
    op.create_table(
        'hotel_suggeriti',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('id_trasferta', sa.Integer, sa.ForeignKey('trasferte.id', ondelete='CASCADE')),
        sa.Column('nome', sa.String, nullable=False),
        sa.Column('lat', sa.Float, nullable=False),
        sa.Column('lon', sa.Float, nullable=False),
        sa.Column('indirizzo', sa.String, nullable=True),
        sa.Column('citta', sa.String, nullable=False)
    )

    # Aggiunta colonne a prenotazioni
    op.add_column('prenotazioni', sa.Column('citta', sa.String, nullable=True))
    op.add_column('prenotazioni', sa.Column('indirizzo', sa.String, nullable=True))


def downgrade() -> None:
    # Rimuove colonne dalla tabella prenotazioni
    op.drop_column('prenotazioni', 'indirizzo')
    op.drop_column('prenotazioni', 'citta')

    # Elimina la tabella hotel_suggeriti
    op.drop_table('hotel_suggeriti')
