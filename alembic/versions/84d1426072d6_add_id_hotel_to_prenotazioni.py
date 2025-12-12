"""Add id_hotel to prenotazioni

Revision ID: 84d1426072d6
Revises: 14d189c655b4
Create Date: 2025-12-12 14:39:08.186779
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84d1426072d6'
down_revision: Union[str, None] = '14d189c655b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ⚡ Aggiungi solo la colonna id_hotel a prenotazioni
    op.add_column('prenotazioni', sa.Column('id_hotel', sa.Integer(), nullable=True))

    # ⚡ Se vuoi creare la FK, con SQLite devi fare attenzione:
    # op.create_foreign_key(
    #     'fk_prenotazioni_hotel',
    #     'prenotazioni',
    #     'hotel_suggeriti',
    #     ['id_hotel'],
    #     ['id']
    # )

    # Rimuoviamo gli ALTER TABLE non compatibili con SQLite
    # (commentati perché causano errori)
    # op.alter_column('hotel_suggeriti', 'location_id',
    #            existing_type=sa.TEXT(),
    #            type_=sa.Integer(),
    #            existing_nullable=True)
    # op.create_foreign_key(None, 'hotel_suggeriti', 'locations', ['location_id'], ['id'])
    # op.alter_column('locations', 'id',
    #            existing_type=sa.INTEGER(),
    #            nullable=False,
    #            autoincrement=True)
    # op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    # op.create_unique_constraint(None, 'locations', ['city_name'])
    # op.alter_column('prenotazioni', 'id_trasferta',
    #            existing_type=sa.INTEGER(),
    #            nullable=False)
    # op.alter_column('prenotazioni', 'tipo_mezzo',
    #            existing_type=sa.VARCHAR(length=5),
    #            nullable=True)
    # op.alter_column('prenotazioni', 'tipo_alloggio',
    #            existing_type=sa.VARCHAR(length=50),
    #            type_=sa.Enum('hotel', 'bnb', 'ostello', 'appartamento', 'casa_vacanze', 'agriturismo', 'guesthouse', 'altro', name='tipoalloggioenum'),
    #            existing_nullable=True)


def downgrade() -> None:
    # Rimuovi la colonna id_hotel in caso di rollback
    op.drop_column('prenotazioni', 'id_hotel')

    # Rimuoviamo anche qui gli ALTER TABLE non compatibili con SQLite
    # (commentati perché causano errori)
    # op.alter_column('prenotazioni', 'tipo_alloggio',
    #            existing_type=sa.Enum('hotel', 'bnb', 'ostello', 'appartamento', 'casa_vacanze', 'agriturismo', 'guesthouse', 'altro', name='tipoalloggioenum'),
    #            type_=sa.VARCHAR(length=50),
    #            existing_nullable=True)
    # op.alter_column('prenotazioni', 'tipo_mezzo',
    #            existing_type=sa.VARCHAR(length=5),
    #            nullable=False)
    # op.alter_column('prenotazioni', 'id_trasferta',
    #            existing_type=sa.INTEGER(),
    #            nullable=True)
