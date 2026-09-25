from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.handlers import database_handler as db_handler


def test_health_check(client: TestClient):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_get_duration_of_stay_reads_cache(client: TestClient, db: Session):
    db_handler.replace_duration_of_stay(
        db,
        include_synthetic=True,
        rows=[
            {
                'visit_date': date(2026, 3, 10),
                'sample_size': 1,
                'avg_duration_minutes': 30.0,
                'median_duration_minutes': 30.0,
                'min_duration_minutes': 30.0,
                'max_duration_minutes': 30.0,
            }
        ],
    )

    response = client.get('/api/stats/duration-of-stay')

    assert response.status_code == 200
    body = response.json()
    assert len(body['series']) == 1
    assert body['series'][0]['sample_size'] == 1


def test_get_duration_of_stay_empty_cache_returns_empty_series(client: TestClient):
    response = client.get('/api/stats/duration-of-stay?include_synthetic=false')

    assert response.status_code == 200
    assert response.json() == {'series': []}


def test_get_rush_hour_reads_cache(client: TestClient, db: Session):
    db_handler.replace_rush_hour(db, include_synthetic=True, rows=[{'hour_of_day': 10, 'visit_count': 5}])

    response = client.get('/api/stats/rush-hour')

    assert response.status_code == 200
    assert response.json()['series'] == [{'hour_of_day': 10, 'visit_count': 5}]


def test_get_monthly_trends_reads_cache(client: TestClient, db: Session):
    db_handler.replace_monthly_trends(
        db, include_synthetic=True, rows=[{'year': 2026, 'month': 1, 'season': 'winter', 'visit_count': 3}]
    )

    response = client.get('/api/stats/monthly-trends')

    assert response.status_code == 200
    assert response.json()['series'] == [{'year': 2026, 'month': 1, 'season': 'winter', 'visit_count': 3}]


def test_get_weekday_trends_reads_cache(client: TestClient, db: Session):
    db_handler.replace_weekday_trends(db, include_synthetic=True, rows=[{'day_of_week': 3, 'visit_count': 7}])

    response = client.get('/api/stats/weekday-trends')

    assert response.status_code == 200
    assert response.json()['series'] == [{'day_of_week': 3, 'visit_count': 7}]


def test_refresh_endpoint_recomputes_and_persists(client: TestClient):
    response = client.post('/api/stats/refresh')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
