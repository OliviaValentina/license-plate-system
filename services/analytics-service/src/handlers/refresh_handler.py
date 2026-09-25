from sqlalchemy.orm import Session

from src.exceptions.database_exceptions import DatabaseError
from src.handlers import database_handler as db_handler
from src.handlers import ingestion_handler
from src.logger import logger


def refresh_all_stats(db: Session) -> None:
    """Recomputes every analytics stat from the ingestion data and replaces the cached
    values in analytics_schema, for both the real-only and real+synthetic data sources.

    Each metric is refreshed independently so that a single failure does not prevent
    the remaining stats from refreshing.

    Args:
        db (Session): db session
    """
    for include_synthetic in (True, False):
        _refresh_duration_of_stay(db, include_synthetic)
        _refresh_rush_hour(db, include_synthetic)
        _refresh_monthly_trends(db, include_synthetic)
        _refresh_weekday_trends(db, include_synthetic)


def _refresh_duration_of_stay(db: Session, include_synthetic: bool) -> None:
    try:
        rows = ingestion_handler.get_duration_of_stay(db, include_synthetic)
        db_handler.replace_duration_of_stay(db, include_synthetic, rows)
        logger.info(f'Refreshed duration of stay stats (include_synthetic={include_synthetic}, {len(rows)} rows)')
    except DatabaseError as e:
        logger.error(f'Failed to refresh duration of stay stats (include_synthetic={include_synthetic}): {e}')


def _refresh_rush_hour(db: Session, include_synthetic: bool) -> None:
    try:
        rows = ingestion_handler.get_rush_hour(db, include_synthetic)
        db_handler.replace_rush_hour(db, include_synthetic, rows)
        logger.info(f'Refreshed rush hour stats (include_synthetic={include_synthetic}, {len(rows)} rows)')
    except DatabaseError as e:
        logger.error(f'Failed to refresh rush hour stats (include_synthetic={include_synthetic}): {e}')


def _refresh_monthly_trends(db: Session, include_synthetic: bool) -> None:
    try:
        rows = ingestion_handler.get_monthly_trends(db, include_synthetic)
        db_handler.replace_monthly_trends(db, include_synthetic, rows)
        logger.info(f'Refreshed monthly trend stats (include_synthetic={include_synthetic}, {len(rows)} rows)')
    except DatabaseError as e:
        logger.error(f'Failed to refresh monthly trend stats (include_synthetic={include_synthetic}): {e}')


def _refresh_weekday_trends(db: Session, include_synthetic: bool) -> None:
    try:
        rows = ingestion_handler.get_weekday_trends(db, include_synthetic)
        db_handler.replace_weekday_trends(db, include_synthetic, rows)
        logger.info(f'Refreshed weekday trend stats (include_synthetic={include_synthetic}, {len(rows)} rows)')
    except DatabaseError as e:
        logger.error(f'Failed to refresh weekday trend stats (include_synthetic={include_synthetic}): {e}')
