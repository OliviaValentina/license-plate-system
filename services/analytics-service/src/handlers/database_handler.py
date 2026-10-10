from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.exceptions.database_exceptions import DatabaseIntegrityError, DatabaseQueryError
from src.models.duration_of_stay_daily import DurationOfStayDaily
from src.models.hourly_visit_stats import HourlyVisitStats
from src.models.monthly_visit_stats import MonthlyVisitStats
from src.models.weekday_visit_stats import WeekdayVisitStats


def _get_cached(db: Session, model, include_synthetic: bool, order_by: tuple) -> list:
    try:
        stmt = select(model).where(model.include_synthetic == include_synthetic).order_by(*order_by)
        return db.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseQueryError(f'Failed to fetch {model.__tablename__}: {e}') from e


def _replace_cached(db: Session, model, include_synthetic: bool, rows: list[dict]) -> None:
    try:
        db.execute(delete(model).where(model.include_synthetic == include_synthetic))
        db.add_all([model(include_synthetic=include_synthetic, **row) for row in rows])
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseIntegrityError(f'Failed to refresh {model.__tablename__}: {e}') from e


def get_duration_of_stay(db: Session, include_synthetic: bool) -> list[DurationOfStayDaily]:
    """Retrieves the cached daily duration-of-stay stats for the given data source."""
    return _get_cached(db, DurationOfStayDaily, include_synthetic, order_by=(DurationOfStayDaily.visit_date,))


def replace_duration_of_stay(db: Session, include_synthetic: bool, rows: list[dict]) -> None:
    """Replaces the cached daily duration-of-stay stats with freshly computed rows."""
    _replace_cached(db, DurationOfStayDaily, include_synthetic, rows)


def get_rush_hour(db: Session, include_synthetic: bool) -> list[HourlyVisitStats]:
    """Retrieves the cached hourly rush-hour stats for the given data source."""
    return _get_cached(db, HourlyVisitStats, include_synthetic, order_by=(HourlyVisitStats.hour_of_day,))


def replace_rush_hour(db: Session, include_synthetic: bool, rows: list[dict]) -> None:
    """Replaces the cached hourly rush-hour stats with freshly computed rows."""
    _replace_cached(db, HourlyVisitStats, include_synthetic, rows)


def get_monthly_trends(db: Session, include_synthetic: bool) -> list[MonthlyVisitStats]:
    """Retrieves the cached monthly/seasonal trend stats for the given data source."""
    return _get_cached(
        db, MonthlyVisitStats, include_synthetic, order_by=(MonthlyVisitStats.year, MonthlyVisitStats.month)
    )


def replace_monthly_trends(db: Session, include_synthetic: bool, rows: list[dict]) -> None:
    """Replaces the cached monthly/seasonal trend stats with freshly computed rows."""
    _replace_cached(db, MonthlyVisitStats, include_synthetic, rows)


def get_weekday_trends(db: Session, include_synthetic: bool) -> list[WeekdayVisitStats]:
    """Retrieves the cached weekday trend stats for the given data source."""
    return _get_cached(db, WeekdayVisitStats, include_synthetic, order_by=(WeekdayVisitStats.day_of_week,))


def replace_weekday_trends(db: Session, include_synthetic: bool, rows: list[dict]) -> None:
    """Replaces the cached weekday trend stats with freshly computed rows."""
    _replace_cached(db, WeekdayVisitStats, include_synthetic, rows)
