"""Add alloggio fields to prenotazioni

Revision ID: 863f984eb9c9
Revises: 25a4b9cf4a4e
Create Date: 2025-11-27 14:44:36.330150
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '863f984eb9c9'
down_revision: Union[str, None] = '25a4b9cf4a4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aggiunge le colonne alloggio alla tabella prenotazioni"""
    op.add_column('prenotazioni', sa.Column('tipo_alloggio', sa.String(length=50), nullable=True))
    op.add_column('prenotazioni', sa.Column('nome_struttura', sa.String(length=100), nullable=True))
    op.add_column('prenotazioni', sa.Column('costo_alloggio', sa.Float(), nullable=True))


def downgrade() -> None:
    """Rimuove le colonne alloggio in caso di rollback"""
    op.drop_column('prenotazioni', 'tipo_alloggio')
    op.drop_column('prenotazioni', 'nome_struttura')
    op.drop_column('prenotazioni', 'costo_alloggio')
