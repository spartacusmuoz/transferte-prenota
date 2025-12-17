from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2025xxxx"
down_revision = "14d189c655b4"
branch_labels = None
depends_on = None


def upgrade():
    # ✅ AGGIUNTA NON DISTRUTTIVA
    op.add_column(
        "hotel_suggeriti",
        sa.Column("image_url", sa.Text(), nullable=True)
    )


def downgrade():
    # rollback pulito
    op.drop_column("hotel_suggeriti", "image_url")
