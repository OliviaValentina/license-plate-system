from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
import os

analytics_metadata = MetaData(schema=os.getenv('ANALYTICS_SCHEMA'))

AnalyticsBase = declarative_base(metadata=analytics_metadata)
