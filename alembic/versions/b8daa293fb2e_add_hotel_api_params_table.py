"""add hotel_api_params table

Revision ID: b8daa293fb2e
Revises: 147a3c7ad4cb
Create Date: 2025-12-03 21:38:33.067666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8daa293fb2e'
down_revision: Union[str, None] = '147a3c7ad4cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### create hotel_api_params table ###
    op.create_table(
        'hotel_api_params',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('id_hotel', sa.Integer(), nullable=False),
        sa.Column('hotel_key', sa.String(), nullable=False),
        sa.Column('chk_in', sa.String(), nullable=False),
        sa.Column('chk_out', sa.String(), nullable=False),
        sa.Column('rooms', sa.Integer(), nullable=True),
        sa.Column('adults', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_hotel'], ['hotel_suggeriti.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_hotel_api_params_id'), 'hotel_api_params', ['id'], unique=False)

    # ### fix prenotazioni.id_trasferta NOT NULL for SQLite ###
    # Step 1: create new table with NOT NULL column
    op.create_table(
        'prenotazioni_new',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('id_trasferta', sa.Integer(), nullable=False),
        sa.Column('tipo_mezzo', sa.VARCHAR(length=5), nullable=True),
        sa.Column('fornitore', sa.String(), nullable=True),
        sa.Column('costo', sa.Float(), nullable=True),
        sa.Column('dettagli', sa.String(), nullable=True),
        sa.Column('file_biglietto', sa.String(), nullable=True),
        sa.Column('tipo_alloggio', sa.Enum('hotel', 'bnb', 'ostello', 'appartamento', 'casa_vacanze', 'agriturismo', 'guesthouse', 'altro', name='tipoalloggioenum'), nullable=True),
        sa.Column('nome_struttura', sa.String(), nullable=True),
        sa.Column('citta', sa.String(), nullable=True),
        sa.Column('costo_alloggio', sa.Float(), nullable=True),
        sa.Column('indirizzo', sa.String(), nullable=True),
        sa.Column('valutazione', sa.Float(), nullable=True),
        sa.Column('numero_recensioni', sa.Integer(), nullable=True),
        sa.Column('link_hotel', sa.String(), nullable=True),
        sa.Column('hotel_key', sa.String(), nullable=True),
    )

    # Step 2: copy data from old table
    op.execute("""
        INSERT INTO prenotazioni_new (
            id, id_trasferta, tipo_mezzo, fornitore, costo, dettagli, file_biglietto,
            tipo_alloggio, nome_struttura, citta, costo_alloggio, indirizzo,
            valutazione, numero_recensioni, link_hotel, hotel_key
        )
        SELECT 
            id, id_trasferta, tipo_mezzo, fornitore, costo, dettagli, file_biglietto,
            tipo_alloggio, nome_struttura, citta, costo_alloggio, indirizzo,
            valutazione, numero_recensioni, link_hotel, hotel_key
        FROM prenotazioni
    """)

    # Step 3: drop old table
    op.drop_table('prenotazioni')

    # Step 4: rename new table
    op.rename_table('prenotazioni_new', 'prenotazioni')


def downgrade() -> None:
    # ### drop hotel_api_params table ###
    op.drop_index(op.f('ix_hotel_api_params_id'), table_name='hotel_api_params')
    op.drop_table('hotel_api_params')

    # ### revert prenotazioni changes ###
    op.create_table(
        'prenotazioni_old',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('id_trasferta', sa.Integer(), nullable=True),
        sa.Column('tipo_mezzo', sa.VARCHAR(length=5), nullable=False),
        sa.Column('fornitore', sa.String(), nullable=True),
        sa.Column('costo', sa.Float(), nullable=True),
        sa.Column('dettagli', sa.String(), nullable=True),
        sa.Column('file_biglietto', sa.String(), nullable=True),
        sa.Column('tipo_alloggio', sa.VARCHAR(length=50), nullable=True),
        sa.Column('nome_struttura', sa.String(), nullable=True),
        sa.Column('citta', sa.String(), nullable=True),
        sa.Column('costo_alloggio', sa.Float(), nullable=True),
        sa.Column('indirizzo', sa.String(), nullable=True),
        sa.Column('valutazione', sa.Float(), nullable=True),
        sa.Column('numero_recensioni', sa.Integer(), nullable=True),
        sa.Column('link_hotel', sa.String(), nullable=True),
        sa.Column('hotel_key', sa.String(), nullable=True),
    )

    op.execute("""
        INSERT INTO prenotazioni_old (
            id, id_trasferta, tipo_mezzo, fornitore, costo, dettagli, file_biglietto,
            tipo_alloggio, nome_struttura, citta, costo_alloggio, indirizzo,
            valutazione, numero_recensioni, link_hotel, hotel_key
        )
        SELECT 
            id, id_trasferta, tipo_mezzo, fornitore, costo, dettagli, file_biglietto,
            tipo_alloggio, nome_struttura, citta, costo_alloggio, indirizzo,
            valutazione, numero_recensioni, link_hotel, hotel_key
        FROM prenotazioni
    """)

    op.drop_table('prenotazioni')
    op.rename_table('prenotazioni_old', 'prenotazioni')
