"""added synthetic vehicle observations table

Revision ID: 58112f34d439
Revises: 5dc1a31469ae
Create Date: 2026-07-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '58112f34d439'
down_revision: Union[str, Sequence[str], None] = '5dc1a31469ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'synthetic_vehicle_observations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('plate_hash', sa.LargeBinary(length=32), nullable=False),
        sa.Column('plate_score', sa.Integer(), nullable=True),
        sa.Column('country_code', sa.String(length=10), nullable=True),
        sa.Column('municipality', sa.String(length=10), nullable=True),
        sa.Column('vehicle_type', sa.String(length=30), nullable=True),
        sa.Column('make', sa.String(length=30), nullable=True),
        sa.Column('model', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=30), nullable=True),
        sa.Column(
            'orientation',
            postgresql.ENUM('FRONT', 'REAR', name='vehicle_orientation', create_type=False),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
        schema='ingestion_schema',
    )
    op.create_index(
        'idx_synthetic_vehicle_observations_plate_hash',
        'synthetic_vehicle_observations',
        ['plate_hash'],
        unique=False,
        schema='ingestion_schema',
    )
    op.create_index(
        'idx_synthetic_vehicle_observations_timestamp',
        'synthetic_vehicle_observations',
        ['timestamp'],
        unique=False,
        schema='ingestion_schema',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'idx_synthetic_vehicle_observations_timestamp',
        table_name='synthetic_vehicle_observations',
        schema='ingestion_schema',
    )
    op.drop_index(
        'idx_synthetic_vehicle_observations_plate_hash',
        table_name='synthetic_vehicle_observations',
        schema='ingestion_schema',
    )
    op.drop_table('synthetic_vehicle_observations', schema='ingestion_schema')
