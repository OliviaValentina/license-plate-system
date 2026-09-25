"""Read-only aggregation queries against ingestion_schema.

No entry/exit session id exists in the raw data, so duration-of-stay is derived by
pairing each FRONT (entry) observation with the chronologically-next REAR (exit)
observation for the same plate_hash, using a LEAD() window function. Rush-hour and
seasonal/weekday stats count FRONT observations only, so each visit is counted once
(counting both orientations would double-count every visit).
"""

from datetime import date, timedelta

from sqlalchemy import Date, Integer, and_, case, cast, func, literal, select, union_all
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db.ingestion_tables import synthetic_vehicle_observations, vehicle_observations
from src.exceptions.database_exceptions import DatabaseQueryError

# Pairs separated by more than this are treated as a missed exit scan rather than a
# genuine visit. The business is open ~10h/day (see generate_synthetic_data.py), so this
# comfortably covers a same-day stay while rejecting multi-day gaps.
MAX_VISIT_DURATION_HOURS = 20

# The stored orientation labels are 'FRONT'/'REAR' - see the note in db/ingestion_tables.py.
ORIENTATION_FRONT = 'FRONT'
ORIENTATION_REAR = 'REAR'


def _observations_cte(include_synthetic: bool):
    """Builds the (optionally UNION ALL'd) set of real + synthetic observations, tagged
    with a `source` column, matching the convention already used by the Grafana
    dashboards."""
    real = select(
        vehicle_observations.c.plate_hash,
        vehicle_observations.c.timestamp,
        vehicle_observations.c.orientation,
        vehicle_observations.c.country_code,
        vehicle_observations.c.municipality,
        vehicle_observations.c.vehicle_type,
        literal('real').label('source'),
    )

    if not include_synthetic:
        return real.cte('obs')

    synthetic = select(
        synthetic_vehicle_observations.c.plate_hash,
        synthetic_vehicle_observations.c.timestamp,
        synthetic_vehicle_observations.c.orientation,
        synthetic_vehicle_observations.c.country_code,
        synthetic_vehicle_observations.c.municipality,
        synthetic_vehicle_observations.c.vehicle_type,
        literal('synthetic').label('source'),
    )

    return union_all(real, synthetic).cte('obs')


# Dimensions a visit-trends line chart can be split into separate series by.
GROUP_BY_COLUMNS = ('vehicle_type', 'country_code', 'municipality')


def _execute(db: Session, stmt) -> list[dict]:
    try:
        return [dict(row) for row in db.execute(stmt).mappings().all()]
    except SQLAlchemyError as e:
        raise DatabaseQueryError(f'Failed to execute analytics aggregation query: {e}') from e


def get_duration_of_stay(
    db: Session,
    include_synthetic: bool,
    start_date: date | None = None,
    end_date: date | None = None,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
) -> list[dict]:
    """Computes the daily average/median/min/max duration of stay, in minutes.

    Args:
        db (Session): db session
        include_synthetic (bool): whether to include synthetic demo data
        start_date (date | None): if given, restrict to visits starting on or after
            this date instead of returning the full history
        end_date (date | None): if given, restrict to visits starting on or before
            this date
        vehicle_type (str | None): if given, restrict to this vehicle type
        country_code (str | None): if given, restrict to this plate country
        municipality (str | None): if given, restrict to this municipality code

    Returns:
        list[dict]: one row per visit_date with sample_size and duration stats
    """
    obs = _observations_cte(include_synthetic)

    next_timestamp = func.lead(obs.c.timestamp).over(
        partition_by=(obs.c.plate_hash, obs.c.source), order_by=obs.c.timestamp
    )
    next_orientation = func.lead(obs.c.orientation).over(
        partition_by=(obs.c.plate_hash, obs.c.source), order_by=obs.c.timestamp
    )

    paired = select(
        obs.c.timestamp.label('entry_time'),
        obs.c.orientation.label('orientation'),
        next_timestamp.label('exit_time'),
        next_orientation.label('next_orientation'),
        obs.c.vehicle_type.label('vehicle_type'),
        obs.c.country_code.label('country_code'),
        obs.c.municipality.label('municipality'),
    ).cte('paired')

    visit_date = cast(paired.c.entry_time, Date)
    duration_minutes = func.extract('epoch', paired.c.exit_time - paired.c.entry_time) / 60.0

    conditions = [
        paired.c.orientation == ORIENTATION_FRONT,
        paired.c.next_orientation == ORIENTATION_REAR,
        paired.c.exit_time > paired.c.entry_time,
        paired.c.exit_time - paired.c.entry_time <= timedelta(hours=MAX_VISIT_DURATION_HOURS),
    ]

    if start_date is not None and end_date is not None and start_date > end_date:
        start_date, end_date = end_date, start_date

    if start_date is not None:
        conditions.append(visit_date >= start_date)
    if end_date is not None:
        conditions.append(visit_date <= end_date)
    if vehicle_type is not None:
        conditions.append(paired.c.vehicle_type == vehicle_type)
    if country_code is not None:
        conditions.append(paired.c.country_code == country_code)
    if municipality is not None:
        conditions.append(paired.c.municipality == municipality)

    stmt = (
        select(
            visit_date.label('visit_date'),
            func.count().label('sample_size'),
            func.avg(duration_minutes).label('avg_duration_minutes'),
            func.percentile_cont(0.5).within_group(duration_minutes).label('median_duration_minutes'),
            func.min(duration_minutes).label('min_duration_minutes'),
            func.max(duration_minutes).label('max_duration_minutes'),
        )
        .where(and_(*conditions))
        .group_by(visit_date)
        .order_by(visit_date)
    )

    return _execute(db, stmt)


def get_rush_hour(
    db: Session,
    include_synthetic: bool,
    start_date: date | None = None,
    end_date: date | None = None,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
) -> list[dict]:
    """Counts entry (FRONT) observations by hour-of-day.

    Args:
        db (Session): db session
        include_synthetic (bool): whether to include synthetic demo data
        start_date (date | None): if given, restrict to visits on or after this date
            instead of returning the full history
        end_date (date | None): if given, restrict to visits on or before this date
        vehicle_type (str | None): if given, restrict to this vehicle type
        country_code (str | None): if given, restrict to this plate country
        municipality (str | None): if given, restrict to this municipality code

    Returns:
        list[dict]: one row per hour_of_day bucket with a visit_count
    """
    obs = _observations_cte(include_synthetic)

    hour_of_day = cast(func.extract('hour', obs.c.timestamp), Integer)
    visit_date = cast(obs.c.timestamp, Date)

    conditions = [obs.c.orientation == ORIENTATION_FRONT]

    if start_date is not None and end_date is not None and start_date > end_date:
        start_date, end_date = end_date, start_date

    if start_date is not None:
        conditions.append(visit_date >= start_date)
    if end_date is not None:
        conditions.append(visit_date <= end_date)
    if vehicle_type is not None:
        conditions.append(obs.c.vehicle_type == vehicle_type)
    if country_code is not None:
        conditions.append(obs.c.country_code == country_code)
    if municipality is not None:
        conditions.append(obs.c.municipality == municipality)

    stmt = (
        select(
            hour_of_day.label('hour_of_day'),
            func.count().label('visit_count'),
        )
        .where(and_(*conditions))
        .group_by(hour_of_day)
        .order_by(hour_of_day)
    )

    return _execute(db, stmt)


def get_monthly_trends(
    db: Session,
    include_synthetic: bool,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
) -> list[dict]:
    """Counts entry (FRONT) observations by year, month, and season.

    Args:
        db (Session): db session
        include_synthetic (bool): whether to include synthetic demo data
        vehicle_type (str | None): if given, restrict to this vehicle type
        country_code (str | None): if given, restrict to this plate country
        municipality (str | None): if given, restrict to this municipality code

    Returns:
        list[dict]: one row per (year, month) bucket with its season and visit_count
    """
    obs = _observations_cte(include_synthetic)

    year = cast(func.extract('year', obs.c.timestamp), Integer)
    month = cast(func.extract('month', obs.c.timestamp), Integer)
    season = case(
        (month.in_([12, 1, 2]), 'winter'),
        (month.in_([3, 4, 5]), 'spring'),
        (month.in_([6, 7, 8]), 'summer'),
        else_='autumn',
    )

    conditions = [obs.c.orientation == ORIENTATION_FRONT]
    if vehicle_type is not None:
        conditions.append(obs.c.vehicle_type == vehicle_type)
    if country_code is not None:
        conditions.append(obs.c.country_code == country_code)
    if municipality is not None:
        conditions.append(obs.c.municipality == municipality)

    stmt = (
        select(
            year.label('year'),
            month.label('month'),
            season.label('season'),
            func.count().label('visit_count'),
        )
        .where(and_(*conditions))
        .group_by(year, month, season)
        .order_by(year, month)
    )

    return _execute(db, stmt)


def get_weekday_trends(
    db: Session,
    include_synthetic: bool,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
) -> list[dict]:
    """Counts entry (FRONT) observations by ISO day-of-week (1=Monday..7=Sunday).

    Args:
        db (Session): db session
        include_synthetic (bool): whether to include synthetic demo data
        vehicle_type (str | None): if given, restrict to this vehicle type
        country_code (str | None): if given, restrict to this plate country
        municipality (str | None): if given, restrict to this municipality code

    Returns:
        list[dict]: one row per day_of_week with a visit_count
    """
    obs = _observations_cte(include_synthetic)

    day_of_week = cast(func.extract('isodow', obs.c.timestamp), Integer)

    conditions = [obs.c.orientation == ORIENTATION_FRONT]
    if vehicle_type is not None:
        conditions.append(obs.c.vehicle_type == vehicle_type)
    if country_code is not None:
        conditions.append(obs.c.country_code == country_code)
    if municipality is not None:
        conditions.append(obs.c.municipality == municipality)

    stmt = (
        select(day_of_week.label('day_of_week'), func.count().label('visit_count'))
        .where(and_(*conditions))
        .group_by(day_of_week)
        .order_by(day_of_week)
    )

    return _execute(db, stmt)


def get_visit_trends(
    db: Session,
    include_synthetic: bool,
    start_date: date | None = None,
    end_date: date | None = None,
    vehicle_type: str | None = None,
    country_code: str | None = None,
    municipality: str | None = None,
    group_by: str | None = None,
) -> list[dict]:
    """Counts entry (FRONT) observations per day, for a line chart, optionally
    filtered by vehicle type / country / (Austrian) municipality and optionally
    split into one series per value of one of those dimensions.

    Args:
        db (Session): db session
        include_synthetic (bool): whether to include synthetic demo data
        start_date (date | None): if given, restrict to visits on or after this date
        end_date (date | None): if given, restrict to visits on or before this date
        vehicle_type (str | None): if given, restrict to this vehicle type
        country_code (str | None): if given, restrict to this plate country
        municipality (str | None): if given, restrict to this municipality code
            (only meaningful together with country_code='AT')
        group_by (str | None): one of 'vehicle_type', 'country_code', 'municipality' -
            if given, returns one row per (visit_date, group_value) so the caller can
            render a multi-line chart; if omitted, returns a single series

    Returns:
        list[dict]: one row per visit_date (and, if group_by is set, per group_value)
            with a visit_count
    """
    if group_by is not None and group_by not in GROUP_BY_COLUMNS:
        raise ValueError(f'group_by must be one of {GROUP_BY_COLUMNS}, got {group_by!r}')

    obs = _observations_cte(include_synthetic)
    visit_date = cast(obs.c.timestamp, Date)

    conditions = [obs.c.orientation == ORIENTATION_FRONT]

    if start_date is not None and end_date is not None and start_date > end_date:
        start_date, end_date = end_date, start_date

    if start_date is not None:
        conditions.append(visit_date >= start_date)
    if end_date is not None:
        conditions.append(visit_date <= end_date)
    if vehicle_type is not None:
        conditions.append(obs.c.vehicle_type == vehicle_type)
    if country_code is not None:
        conditions.append(obs.c.country_code == country_code)
    if municipality is not None:
        conditions.append(obs.c.municipality == municipality)

    group_cols = [visit_date]
    select_cols = [visit_date.label('visit_date')]
    if group_by is not None:
        group_col = getattr(obs.c, group_by)
        select_cols.append(group_col.label('group_value'))
        group_cols.append(group_col)
    select_cols.append(func.count().label('visit_count'))

    stmt = select(*select_cols).where(and_(*conditions)).group_by(*group_cols).order_by(*group_cols)

    return _execute(db, stmt)


def get_filter_options(db: Session, include_synthetic: bool) -> dict:
    """Lists the distinct vehicle types, plate countries, and (country, municipality)
    pairs present in the observations, to populate analytics filter dropdowns.

    Args:
        db (Session): db session
        include_synthetic (bool): whether to include synthetic demo data

    Returns:
        dict: {'vehicle_types': [...], 'country_codes': [...], 'municipalities': [...]}
            where municipalities is a list of {'country_code', 'municipality'} pairs
    """
    obs = _observations_cte(include_synthetic)

    try:
        vehicle_types = (
            db.execute(
                select(obs.c.vehicle_type)
                .where(obs.c.vehicle_type.isnot(None))
                .distinct()
                .order_by(obs.c.vehicle_type)
            )
            .scalars()
            .all()
        )
        country_codes = (
            db.execute(
                select(obs.c.country_code)
                .where(obs.c.country_code.isnot(None))
                .distinct()
                .order_by(obs.c.country_code)
            )
            .scalars()
            .all()
        )
        municipality_rows = db.execute(
            select(obs.c.country_code, obs.c.municipality)
            .where(obs.c.municipality.isnot(None))
            .distinct()
            .order_by(obs.c.country_code, obs.c.municipality)
        ).all()
    except SQLAlchemyError as e:
        raise DatabaseQueryError(f'Failed to execute analytics aggregation query: {e}') from e

    return {
        'vehicle_types': list(vehicle_types),
        'country_codes': list(country_codes),
        'municipalities': [
            {'country_code': row.country_code, 'municipality': row.municipality} for row in municipality_rows
        ],
    }
