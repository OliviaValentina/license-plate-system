from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

# relative imports needed for db-prestart service
from ..models.base import AnalyticsBase


class MonthlyVisitStats(AnalyticsBase):
    """SQLAlchemy model for the monthly/seasonal visit statistics

    Args:
        AnalyticsBase (postgres schema): base for the analytics schema
    """

    __tablename__ = 'monthly_visit_stats'
    __table_args__ = (
        UniqueConstraint('year', 'month', 'include_synthetic', name='uq_monthly_visit_stats_year_month_source'),
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    year = Column(
        Integer,
        nullable=False,
        index=True,
    )
    month = Column(
        Integer,
        nullable=False,
        index=True,
    )
    season = Column(
        String(10),
        nullable=False,
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
