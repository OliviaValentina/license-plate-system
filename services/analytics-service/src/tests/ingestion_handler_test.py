from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from src.db.ingestion_tables import synthetic_vehicle_observations
from src.handlers import ingestion_handler
from src.tests.conftest import AdminDb

PLATE_A = b'A' * 32
PLATE_B = b'B' * 32
PLATE_C = b'C' * 32


def _insert_observation(admin_db: AdminDb, plate_hash: bytes, timestamp: datetime, orientation: str) -> None:
    admin_db.insert_observation(
        synthetic_vehicle_observations, plate_hash=plate_hash, timestamp=timestamp, orientation=orientation
    )


def _rows_for_visit_date(db: Session, include_synthetic: bool, visit_date) -> list[dict]:
    """Aggregation queries return full history, so tests scope the result down to the
    single visit_date they seeded, keeping them independent of whatever other data
    (real or synthetic) already exists in the shared dev/CI database."""
    rows = ingestion_handler.get_duration_of_stay(db, include_synthetic=include_synthetic)
    return [row for row in rows if row['visit_date'] == visit_date]


def test_get_duration_of_stay_pairs_front_and_rear(db: Session, admin_db: AdminDb):
    """A FRONT immediately followed by a REAR for the same plate is paired and its
    duration (in minutes) reported."""
    entry = datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc)
    exit_time = entry + timedelta(minutes=45)

    _insert_observation(admin_db, PLATE_A, entry, 'FRONT')
    _insert_observation(admin_db, PLATE_A, exit_time, 'REAR')

    rows = _rows_for_visit_date(db, include_synthetic=True, visit_date=entry.date())

    assert len(rows) == 1
    assert rows[0]['sample_size'] == 1
    assert rows[0]['avg_duration_minutes'] == pytest.approx(45.0)


def test_get_duration_of_stay_ignores_unpaired_front(db: Session, admin_db: AdminDb):
    """A FRONT with no following REAR is excluded rather than guessed at."""
    entry = datetime(2026, 3, 17, 9, 0, tzinfo=timezone.utc)
    _insert_observation(admin_db, PLATE_B, entry, 'FRONT')

    rows = _rows_for_visit_date(db, include_synthetic=True, visit_date=entry.date())

    assert rows == []


def test_get_duration_of_stay_ignores_gap_over_max_duration(db: Session, admin_db: AdminDb):
    """A FRONT followed by a REAR more than MAX_VISIT_DURATION_HOURS later (a missed
    exit scan) is excluded."""
    entry = datetime(2026, 3, 24, 9, 0, tzinfo=timezone.utc)
    exit_time = entry + timedelta(hours=ingestion_handler.MAX_VISIT_DURATION_HOURS + 1)

    _insert_observation(admin_db, PLATE_C, entry, 'FRONT')
    _insert_observation(admin_db, PLATE_C, exit_time, 'REAR')

    rows = _rows_for_visit_date(db, include_synthetic=True, visit_date=entry.date())

    assert rows == []


def test_get_duration_of_stay_pairs_two_visits_same_day(db: Session, admin_db: AdminDb):
    """A plate visiting twice in one day produces two separately paired visits."""
    first_entry = datetime(2026, 3, 31, 9, 0, tzinfo=timezone.utc)
    first_exit = first_entry + timedelta(minutes=20)
    second_entry = first_exit + timedelta(hours=2)
    second_exit = second_entry + timedelta(minutes=30)

    for ts, orientation in (
        (first_entry, 'FRONT'),
        (first_exit, 'REAR'),
        (second_entry, 'FRONT'),
        (second_exit, 'REAR'),
    ):
        _insert_observation(admin_db, PLATE_A, ts, orientation)

    rows = _rows_for_visit_date(db, include_synthetic=True, visit_date=first_entry.date())

    assert len(rows) == 1
    assert rows[0]['sample_size'] == 2


def test_get_rush_hour_counts_front_only(db: Session, admin_db: AdminDb):
    """Rush-hour counts entries (FRONT) once each, not their paired exits. Rush-hour
    aggregates across all history, so this asserts the delta caused by the seeded rows
    rather than an exact total (which would depend on whatever else is in the table)."""
    entry = datetime(2026, 4, 7, 9, 30, tzinfo=timezone.utc)  # a Tuesday
    exit_time = entry + timedelta(minutes=15)

    def _bucket_count() -> int:
        rows = ingestion_handler.get_rush_hour(db, include_synthetic=True)
        matches = [r['visit_count'] for r in rows if r['hour_of_day'] == 9]
        return matches[0] if matches else 0

    before = _bucket_count()

    _insert_observation(admin_db, PLATE_A, entry, 'FRONT')
    _insert_observation(admin_db, PLATE_A, exit_time, 'REAR')

    after = _bucket_count()

    assert after == before + 1


def test_get_rush_hour_filters_by_date_range(db: Session, admin_db: AdminDb):
    """Rows outside the given [start_date, end_date] are excluded, and hour buckets no
    longer distinguish weekday from weekend."""
    in_range = datetime(2026, 5, 5, 14, 0, tzinfo=timezone.utc)  # a Tuesday
    out_of_range = datetime(2026, 5, 20, 14, 0, tzinfo=timezone.utc)

    _insert_observation(admin_db, PLATE_A, in_range, 'FRONT')
    _insert_observation(admin_db, PLATE_B, out_of_range, 'FRONT')

    rows = ingestion_handler.get_rush_hour(
        db, include_synthetic=True, start_date=date(2026, 5, 1), end_date=date(2026, 5, 10)
    )

    assert all('is_weekend' not in row for row in rows)
    matches = [r['visit_count'] for r in rows if r['hour_of_day'] == 14]
    assert matches == [1]


def test_get_weekday_trends_counts_by_iso_day(db: Session, admin_db: AdminDb):
    """Weekday trends bucket by ISO day-of-week (1=Monday..7=Sunday), aggregated across
    all history, so this asserts the delta caused by the seeded row."""
    monday = datetime(2026, 4, 6, 10, 0, tzinfo=timezone.utc)  # 2026-04-06 is a Monday

    def _bucket_count() -> int:
        rows = ingestion_handler.get_weekday_trends(db, include_synthetic=True)
        matches = [r['visit_count'] for r in rows if r['day_of_week'] == 1]
        return matches[0] if matches else 0

    before = _bucket_count()

    _insert_observation(admin_db, PLATE_A, monday, 'FRONT')

    after = _bucket_count()

    assert after == before + 1


def test_get_monthly_trends_assigns_season(db: Session, admin_db: AdminDb):
    """Monthly trends label each month with its season, aggregated across all history,
    so this asserts the delta caused by the seeded row."""
    winter_day = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)

    def _bucket() -> dict | None:
        rows = ingestion_handler.get_monthly_trends(db, include_synthetic=True)
        matches = [r for r in rows if r['year'] == 2026 and r['month'] == 1]
        return matches[0] if matches else None

    before = _bucket()
    before_count = before['visit_count'] if before else 0

    _insert_observation(admin_db, PLATE_A, winter_day, 'FRONT')

    after = _bucket()

    assert after is not None
    assert after['season'] == 'winter'
    assert after['visit_count'] == before_count + 1


def test_include_synthetic_false_excludes_synthetic_rows(db: Session, admin_db: AdminDb):
    """Setting include_synthetic=False excludes rows from synthetic_vehicle_observations."""
    entry = datetime(2026, 4, 14, 9, 0, tzinfo=timezone.utc)

    def _bucket_count() -> int:
        rows = ingestion_handler.get_rush_hour(db, include_synthetic=False)
        matches = [r['visit_count'] for r in rows if r['hour_of_day'] == 9]
        return matches[0] if matches else 0

    before = _bucket_count()

    _insert_observation(admin_db, PLATE_A, entry, 'FRONT')

    after = _bucket_count()

    assert after == before
