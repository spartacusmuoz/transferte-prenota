"""Aggiunta colonna hotel_key a HotelSuggerito

Revision ID: xxxx_add_hotel_key_to_hotel_suggeriti
Revises: c106ec18dbaa
Create Date: 2025-12-03 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx_add_hotel_key_to_hotel_suggeriti'
down_revision = 'c106ec18dbaa'
branch_labels = None
depends_on = None

def upgrade():
    # Aggiunge la colonna hotel_key alla tabella hotel_suggeriti
    op.add_column('hotel_suggeriti', sa.Column('hotel_key', sa.String(), nullable=True))

def downgrade():
    # Rimuove la colonna hotel_key se serve fare rollback
    op.drop_column('hotel_suggeriti', 'hotel_key')
