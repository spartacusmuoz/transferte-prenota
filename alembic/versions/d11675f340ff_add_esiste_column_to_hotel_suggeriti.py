"""add esiste column to hotel_suggeriti

Revision ID: d11675f340ff
Revises: 7f964633c6e3
Create Date: 2025-12-08 08:49:20.891127
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd11675f340ff'
down_revision = '7f964633c6e3'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # aggiunge la colonna 'esiste' alla tabella 'hotel_suggeriti'
    op.add_column('hotel_suggeriti', sa.Column('esiste', sa.Boolean(), nullable=True, server_default=sa.false()))

def downgrade() -> None:
    # rimuove la colonna 'esiste'
    op.drop_column('hotel_suggeriti', 'esiste')
