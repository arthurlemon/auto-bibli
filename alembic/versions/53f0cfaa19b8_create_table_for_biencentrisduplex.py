"""Create table for BienCentrisDuplex

Revision ID: 53f0cfaa19b8
Revises:
Create Date: 2024-12-28 08:37:03.508192

"""

from typing import Sequence, Union
from centris.backend.utils import get_default_date
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "53f0cfaa19b8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Alembic migration commands
def upgrade():
    op.create_table(
        "plex_centris_listings",
        sa.Column("centris_id", sa.Integer, primary_key=True),
        sa.Column("url", sa.String, nullable=False),
        sa.Column("title", sa.String, nullable=True),
        sa.Column("annee_construction", sa.Integer, nullable=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("unites", sa.String, nullable=True),
        sa.Column("nombre_unites", sa.Integer, nullable=True),
        sa.Column("superficie_habitable", sa.Integer, nullable=True),
        sa.Column("superficie_batiment", sa.Integer, nullable=True),
        sa.Column("superficie_commerce", sa.Integer, nullable=True),
        sa.Column("superficie_terrain", sa.Integer, nullable=True),
        sa.Column("stationnement", sa.Integer, nullable=True),
        sa.Column("utilisation", sa.String, nullable=True),
        sa.Column("style_batiment", sa.String, nullable=True),
        sa.Column("adresse", sa.String, nullable=True),
        sa.Column("ville", sa.String, nullable=True),
        sa.Column("quartier", sa.String, nullable=True),
        sa.Column("prix", sa.Integer, nullable=False),
        sa.Column("revenus", sa.Integer, nullable=True),
        sa.Column("taxes", sa.Integer, nullable=True),
        sa.Column("eval_municipale", sa.Integer, nullable=True),
        sa.Column("date_scrape", sa.String, nullable=False, default=get_default_date),
    )


def downgrade():
    op.drop_table("plex_centris_listings")
