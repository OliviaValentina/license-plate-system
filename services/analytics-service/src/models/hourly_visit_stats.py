from sqlalchemy import Boolean, Column, DateTime, Integer, UniqueConstraint
from sqlalchemy.sql import func

# relative imports needed for db-prestart service
from ..models.base import AnalyticsBase


class HourlyVisitStats(AnalyticsBase):
    """SQLAlchemy model for the hourly rush-hour statistics

    Args:
        AnalyticsBase (postgres schema): base for the analytics schema
    """

    __tablename__ = 'hourly_visit_stats'
    __table_args__ = (
        UniqueConstraint('hour_of_day', 'include_synthetic', name='uq_hourly_visit_stats_hour_source'),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    hour_of_day = Column(
        Integer,
        nullable=False,
        index=True,
    )
    include_synthetic = Column(
        Boolean,
        nullable=False,
        index=True,
    )
    visit_count = Column(
        Integer,
        nullable=False,
    )
    computed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
