"""aggiunta colonne hotel

Revision ID: 5af04c44d614
Revises: 863f984eb9c9
Create Date: 2025-11-28 15:12:28.994759

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5af04c44d614'
down_revision: Union[str, None] = '863f984eb9c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Aggiungi colonne hotel alla tabella prenotazioni
    op.add_column('prenotazioni', sa.Column('indirizzo', sa.String(), nullable=True))
    op.add_column('prenotazioni', sa.Column('valutazione', sa.Float(), nullable=True))
    op.add_column('prenotazioni', sa.Column('numero_recensioni', sa.Integer(), nullable=True))
    op.add_column('prenotazioni', sa.Column('link_hotel', sa.String(), nullable=True))


def downgrade() -> None:
    # Rimuovi colonne se si fa il rollback
    op.drop_column('prenotazioni', 'link_hotel')
    op.drop_column('prenotazioni', 'numero_recensioni')
    op.drop_column('prenotazioni', 'valutazione')
    op.drop_column('prenotazioni', 'indirizzo')
