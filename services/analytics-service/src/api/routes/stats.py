from datetime import date

from fastapi import APIRouter, HTTPException, status

from src.db.session import SessionDep
from src.exceptions.database_exceptions import DatabaseError, DatabaseIntegrityError, DatabaseQueryError
import src.handlers.database_handler as db_handler
import src.handlers.ingestion_handler as ingestion_handler
from src.handlers.refresh_handler import refresh_all_stats
import src.schemas.common as common_schemas
import src.schemas.duration_of_stay as duration_of_stay_schemas
import src.schemas.rush_hour as rush_hour_schemas
import src.schemas.seasonal as seasonal_schemas
import src.schemas.visit_trends as visit_trends_schemas
from src.handlers.ingestion_handler import GROUP_BY_COLUMNS

router = APIRouter()


def _raise_http_from_database_error(err: DatabaseError) -> None:
    if isinstance(err, (DatabaseIntegrityError, DatabaseQueryError)):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    # Fallback for any other DatabaseError
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'An unexpected database error occurred: {err}'
    )


@router.get('/duration-of-stay', response_model=duration_of_stay_schemas.DurationOfStayResponse)
def get_duration_of_stay(
    db: SessionDep,
    include_synthetic: bool = True,
    start_date: date | None = None,
    end_date: date | None = None,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
):
    """
    Retrieve average/median/min/max duration of stay per day.

    Args:
        db (SessionDep): Database session dependency
        include_synthetic (bool): whether to include synthetic demo data
        start_date (date | None): if given together with end_date, computes live over
            that date range instead of reading the periodically-refreshed cache
        end_date (date | None): if given together with start_date, computes live over
            that date range instead of reading the periodically-refreshed cache
        vehicle_type (str | None): if given, computes live, restricted to this vehicle type
        country_code (str | None): if given, computes live, restricted to this plate country
        municipality (str | None): if given, computes live, restricted to this municipality code

    Returns:
        duration_of_stay_schemas.DurationOfStayResponse: the daily duration-of-stay series
    """
    try:
        if any(v is not None for v in (start_date, end_date, vehicle_type, country_code, municipality)):
            rows = ingestion_handler.get_duration_of_stay(
                db,
                include_synthetic,
                start_date=start_date,
                end_date=end_date,
                vehicle_type=vehicle_type,
                country_code=country_code,
                municipality=municipality,
            )
            return {'series': rows}
        return {'series': db_handler.get_duration_of_stay(db, include_synthetic)}
    except DatabaseError as e:
        _raise_http_from_database_error(e)


@router.get('/rush-hour', response_model=rush_hour_schemas.RushHourResponse)
def get_rush_hour(
    db: SessionDep,
    include_synthetic: bool = True,
    start_date: date | None = None,
    end_date: date | None = None,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
):
    """
    Retrieve visit counts by hour-of-day.

    Args:
        db (SessionDep): Database session dependency
        include_synthetic (bool): whether to include synthetic demo data
        start_date (date | None): if given together with end_date, computes live over
            that date range instead of reading the periodically-refreshed cache
        end_date (date | None): if given together with start_date, computes live over
            that date range instead of reading the periodically-refreshed cache
        vehicle_type (str | None): if given, computes live, restricted to this vehicle type
        country_code (str | None): if given, computes live, restricted to this plate country
        municipality (str | None): if given, computes live, restricted to this municipality code

    Returns:
        rush_hour_schemas.RushHourResponse: the hourly visit-count series
    """
    try:
        if any(v is not None for v in (start_date, end_date, vehicle_type, country_code, municipality)):
            rows = ingestion_handler.get_rush_hour(
                db,
                include_synthetic,
                start_date=start_date,
                end_date=end_date,
                vehicle_type=vehicle_type,
                country_code=country_code,
                municipality=municipality,
            )
            return {'series': rows}
        return {'series': db_handler.get_rush_hour(db, include_synthetic)}
    except DatabaseError as e:
        _raise_http_from_database_error(e)


@router.get('/monthly-trends', response_model=seasonal_schemas.MonthlyTrendsResponse)
def get_monthly_trends(
    db: SessionDep,
    include_synthetic: bool = True,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
):
    """
    Retrieve visit counts by year, month, and season.

    Args:
        db (SessionDep): Database session dependency
        include_synthetic (bool): whether to include synthetic demo data
        vehicle_type (str | None): if given, computes live, restricted to this vehicle type
        country_code (str | None): if given, computes live, restricted to this plate country
        municipality (str | None): if given, computes live, restricted to this municipality code

    Returns:
        seasonal_schemas.MonthlyTrendsResponse: the monthly/seasonal visit-count series
    """
    try:
        if any(v is not None for v in (vehicle_type, country_code, municipality)):
            rows = ingestion_handler.get_monthly_trends(
                db,
                include_synthetic,
                vehicle_type=vehicle_type,
                country_code=country_code,
                municipality=municipality,
            )
            return {'series': rows}
        return {'series': db_handler.get_monthly_trends(db, include_synthetic)}
    except DatabaseError as e:
        _raise_http_from_database_error(e)


@router.get('/weekday-trends', response_model=seasonal_schemas.WeekdayTrendsResponse)
def get_weekday_trends(
    db: SessionDep,
    include_synthetic: bool = True,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
):
    """
    Retrieve visit counts by day of week.

    Args:
        db (SessionDep): Database session dependency
        include_synthetic (bool): whether to include synthetic demo data
        vehicle_type (str | None): if given, computes live, restricted to this vehicle type
        country_code (str | None): if given, computes live, restricted to this plate country
        municipality (str | None): if given, computes live, restricted to this municipality code

    Returns:
        seasonal_schemas.WeekdayTrendsResponse: the weekday visit-count series
    """
    try:
        if any(v is not None for v in (vehicle_type, country_code, municipality)):
            rows = ingestion_handler.get_weekday_trends(
                db,
                include_synthetic,
                vehicle_type=vehicle_type,
                country_code=country_code,
                municipality=municipality,
            )
            return {'series': rows}
        return {'series': db_handler.get_weekday_trends(db, include_synthetic)}
    except DatabaseError as e:
        _raise_http_from_database_error(e)


@router.get('/visit-trends', response_model=visit_trends_schemas.VisitTrendsResponse)
def get_visit_trends(
    db: SessionDep,
    include_synthetic: bool = True,
    start_date: date | None = None,
    end_date: date | None = None,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
    group_by: str | None = None,
):
    """
    Retrieve daily visit counts, optionally filtered by vehicle type, plate country,
    or (Austrian) municipality, and optionally split into one series per value of one
    of those dimensions for a multi-line chart.

    Args:
        db (SessionDep): Database session dependency
        include_synthetic (bool): whether to include synthetic demo data
        start_date (date | None): if given, restrict to visits on or after this date
        end_date (date | None): if given, restrict to visits on or before this date
        vehicle_type (str | None): if given, restrict to this vehicle type
        country_code (str | None): if given, restrict to this plate country
        municipality (str | None): if given, restrict to this municipality code
        group_by (str | None): one of 'vehicle_type', 'country_code', 'municipality' -
            splits the series by this dimension instead of returning a single line

    Returns:
        visit_trends_schemas.VisitTrendsResponse: the daily visit-count series
    """
    if group_by is not None and group_by not in GROUP_BY_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'group_by must be one of {sorted(GROUP_BY_COLUMNS)}',
        )
    try:
        rows = ingestion_handler.get_visit_trends(
            db,
            include_synthetic,
            start_date=start_date,
            end_date=end_date,
            vehicle_type=vehicle_type,
            country_code=country_code,
            municipality=municipality,
            group_by=group_by,
        )
        return {'series': rows}
    except DatabaseError as e:
        _raise_http_from_database_error(e)


@router.get('/filter-options', response_model=visit_trends_schemas.FilterOptionsResponse)
def get_filter_options(db: SessionDep, include_synthetic: bool = True):
    """
    Retrieve the distinct vehicle types, plate countries, and municipalities present
    in the observations, to populate analytics filter dropdowns.

    Args:
        db (SessionDep): Database session dependency
        include_synthetic (bool): whether to include synthetic demo data

    Returns:
        visit_trends_schemas.FilterOptionsResponse: available filter values
    """
    try:
        return ingestion_handler.get_filter_options(db, include_synthetic)
    except DatabaseError as e:
        _raise_http_from_database_error(e)


@router.post('/refresh', response_model=common_schemas.RefreshResponse)
def refresh_stats(db: SessionDep):
    """
    Force an immediate recompute of all cached analytics stats.

    Args:
        db (SessionDep): Database session dependency

    Returns:
        common_schemas.RefreshResponse: confirmation that the refresh ran
    """
    try:
        refresh_all_stats(db)
        return {'status': 'ok'}
    except DatabaseError as e:
        _raise_http_from_database_error(e)
