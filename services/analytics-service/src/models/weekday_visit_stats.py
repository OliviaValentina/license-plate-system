from sqlalchemy import Boolean, Column, DateTime, Integer, UniqueConstraint
from sqlalchemy.sql import func

# relative imports needed for db-prestart service
from ..models.base import AnalyticsBase


class WeekdayVisitStats(AnalyticsBase):
    """SQLAlchemy model for the day-of-week visit statistics

    Args:
        AnalyticsBase (postgres schema): base for the analytics schema
    """

    __tablename__ = 'weekday_visit_stats'
    __table_args__ = (UniqueConstraint('day_of_week', 'include_synthetic', name='uq_weekday_visit_stats_day_source'),)

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    day_of_week = Column(
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
