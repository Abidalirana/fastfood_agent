"""Create full agent_sessions table

Revision ID: d24ade9b604e
Revises: 65aab6511ff4
Create Date: 2025-08-05 02:00:01.688366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd24ade9b604e'
down_revision: Union[str, Sequence[str], None] = '65aab6511ff4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
