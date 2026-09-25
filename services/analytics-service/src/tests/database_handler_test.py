from datetime import date

from sqlalchemy.orm import Session

from src.handlers import database_handler as db_handler

DURATION_ROW = {
    'visit_date': date(2026, 3, 10),
    'sample_size': 3,
    'avg_duration_minutes': 42.0,
    'median_duration_minutes': 40.0,
    'min_duration_minutes': 20.0,
    'max_duration_minutes': 70.0,
}


def test_replace_and_get_duration_of_stay(db: Session):
    db_handler.replace_duration_of_stay(db, include_synthetic=True, rows=[DURATION_ROW])
    cached = db_handler.get_duration_of_stay(db, include_synthetic=True)

    assert len(cached) == 1
    assert cached[0].visit_date == date(2026, 3, 10)
    assert cached[0].sample_size == 3


def test_replace_duration_of_stay_overwrites_previous_values(db: Session):
    """A second refresh fully replaces the previous cached rows for that data source."""
    db_handler.replace_duration_of_stay(db, include_synthetic=True, rows=[DURATION_ROW])
    db_handler.replace_duration_of_stay(
        db,
        include_synthetic=True,
        rows=[{**DURATION_ROW, 'visit_date': date(2026, 3, 11), 'sample_size': 2}],
    )

    cached = db_handler.get_duration_of_stay(db, include_synthetic=True)

    assert len(cached) == 1
    assert cached[0].visit_date == date(2026, 3, 11)
    assert cached[0].sample_size == 2


def test_replace_duration_of_stay_keeps_other_data_source_untouched(db: Session):
    """Refreshing the synthetic-included cache does not affect the real-only cache."""
    db_handler.replace_duration_of_stay(db, include_synthetic=True, rows=[DURATION_ROW])
    db_handler.replace_duration_of_stay(
        db,
        include_synthetic=False,
        rows=[{**DURATION_ROW, 'visit_date': date(2026, 3, 12)}],
    )

    with_synthetic = db_handler.get_duration_of_stay(db, include_synthetic=True)
    real_only = db_handler.get_duration_of_stay(db, include_synthetic=False)

    assert len(with_synthetic) == 1
    assert len(real_only) == 1
    assert with_synthetic[0].visit_date != real_only[0].visit_date


def test_replace_and_get_rush_hour(db: Session):
    db_handler.replace_rush_hour(db, include_synthetic=True, rows=[{'hour_of_day': 9, 'visit_count': 12}])
    cached = db_handler.get_rush_hour(db, include_synthetic=True)

    assert len(cached) == 1
    assert cached[0].hour_of_day == 9
    assert cached[0].visit_count == 12


def test_replace_and_get_monthly_trends(db: Session):
    db_handler.replace_monthly_trends(
        db, include_synthetic=True, rows=[{'year': 2026, 'month': 7, 'season': 'summer', 'visit_count': 100}]
    )
    cached = db_handler.get_monthly_trends(db, include_synthetic=True)

    assert len(cached) == 1
    assert cached[0].season == 'summer'


def test_replace_and_get_weekday_trends(db: Session):
    db_handler.replace_weekday_trends(db, include_synthetic=True, rows=[{'day_of_week': 1, 'visit_count': 50}])
    cached = db_handler.get_weekday_trends(db, include_synthetic=True)

    assert len(cached) == 1
    assert cached[0].day_of_week == 1
