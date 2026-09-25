"""Read-only SQLAlchemy Core table definitions for the ingestion_schema tables.

These are deliberately plain Core `Table` objects, not ORM models imported from
data-collection-service, so analytics-service has no Python import dependency on
another service. `analytics_user` only ever has SELECT privileges on this schema
(see db/init.sql), so no create/insert/update logic is defined here.
"""

from sqlalchemy import Column, DateTime, Integer, LargeBinary, MetaData, String, Table
from sqlalchemy.dialects.postgresql import ENUM

from src.config import settings

ingestion_metadata = MetaData(schema=settings.data_collection_schema)

# create_type=False: the enum type already exists (created by data-collection-service's
# migrations) - this table definition must never attempt to create or alter it.
#
# The stored labels are 'FRONT'/'REAR' (the Python enum *names*), not 'front'/'rear'
# (the values) - data-collection-service defines this column as
# ENUM(VehicleOrientation, name='vehicle_orientation'), and SQLAlchemy's postgresql
# ENUM defaults to using Enum member names as the on-the-wire representation.
_vehicle_orientation = ENUM('FRONT', 'REAR', name='vehicle_orientation', create_type=False)

vehicle_observations = Table(
    'vehicle_observations',
    ingestion_metadata,
    Column('id', Integer, primary_key=True),
    Column('timestamp', DateTime(timezone=True)),
    Column('plate_hash', LargeBinary(32)),
    Column('orientation', _vehicle_orientation),
    Column('country_code', String(10)),
    Column('municipality', String(10)),
    Column('vehicle_type', String(30)),
)

synthetic_vehicle_observations = Table(
    'synthetic_vehicle_observations',
    ingestion_metadata,
    Column('id', Integer, primary_key=True),
    Column('timestamp', DateTime(timezone=True)),
    Column('plate_hash', LargeBinary(32)),
    Column('orientation', _vehicle_orientation),
    Column('country_code', String(10)),
    Column('municipality', String(10)),
    Column('vehicle_type', String(30)),
)
