"""remove category

Revision ID: b939b39395e2
Revises: 5fae8870072a
Create Date: 2026-02-02 11:57:35.643537

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b939b39395e2"
down_revision: Union[str, Sequence[str], None] = "5fae8870072a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index("idx_audio_user_category", table_name="audio_files")

    op.drop_column("audio_files", "category")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "audio_files",
        sa.Column(
            "category",
            postgresql.ENUM("QURAN", "LECTURE", "REMINDER", name="audiocategory"),
            nullable=True,
        ),
    )

    op.create_index("idx_audio_user_category", "audio_files", ["user_id", "category"])
