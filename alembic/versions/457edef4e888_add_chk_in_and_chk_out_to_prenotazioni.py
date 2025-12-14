from alembic import op
import sqlalchemy as sa

revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None
down_revision = None


def upgrade():
    op.add_column(
        'prenotazioni',
        sa.Column('chk_in', sa.Date(), nullable=True)
    )
    op.add_column(
        'prenotazioni',
        sa.Column('chk_out', sa.Date(), nullable=True)
    )


def downgrade():
    op.drop_column('prenotazioni', 'chk_out')
    op.drop_column('prenotazioni', 'chk_in')
