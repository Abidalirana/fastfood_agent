"""unified schema

Revision ID: 65aab6511ff4
Revises: 2161a4cb7176
Create Date: 2025-08-05 01:03:38.997848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65aab6511ff4'
down_revision: Union[str, Sequence[str], None] = '2161a4cb7176'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
