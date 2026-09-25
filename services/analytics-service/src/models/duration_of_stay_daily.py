from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, UniqueConstraint
from sqlalchemy.sql import func

# relative imports needed for db-prestart service
from ..models.base import AnalyticsBase


class DurationOfStayDaily(AnalyticsBase):
    """SQLAlchemy model for the daily duration-of-stay statistics

    Args:
        AnalyticsBase (postgres schema): base for the analytics schema
    """

    __tablename__ = 'duration_of_stay_daily'
    __table_args__ = (
        UniqueConstraint('visit_date', 'include_synthetic', name='uq_duration_of_stay_daily_date_source'),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    visit_date = Column(
        Date,
        nullable=False,
        index=True,
    )
    include_synthetic = Column(
        Boolean,
        nullable=False,
        index=True,
    )
    sample_size = Column(
        Integer,
        nullable=False,
    )
    avg_duration_minutes = Column(
        Float,
        nullable=False,
    )
    median_duration_minutes = Column(
        Float,
        nullable=False,
    )
    min_duration_minutes = Column(
        Float,
        nullable=False,
    )
    max_duration_minutes = Column(
        Float,
        nullable=False,
    )
    computed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
