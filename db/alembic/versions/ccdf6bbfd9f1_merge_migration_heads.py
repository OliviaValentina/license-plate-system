"""merge migration heads

Revision ID: ccdf6bbfd9f1
Revises: 97b047fbba19, 58112f34d439
Create Date: 2026-09-14 13:49:32.711270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccdf6bbfd9f1'
down_revision: Union[str, Sequence[str], None] = ('97b047fbba19', '58112f34d439')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
