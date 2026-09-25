"""Generates artificial vehicle observation data for testing and demos.

Populates `synthetic_vehicle_observations` with data shaped like the real
observations collected from the plate recognizer: every simulated plate gets
exactly one "entry" (orientation=front) and one "exit" (orientation=rear)
observation per day, both falling between 09:00-19:00 on days Monday through
Saturday (opening hours of zotter).

Run inside the data-collection-service container, which already has the
required DB_* environment variables set:

    docker compose -f docker-compose.dev.yaml exec data-collection-service \\
        python -m src.scripts.generate_synthetic_data --plates 25 --weeks 4
"""

from __future__ import annotations

import argparse
import json
import os
import random
import string
from datetime import date, datetime, time, timedelta
from hashlib import sha256
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.enums.vehicle_orientation import VehicleOrientation
from src.models.synthetic_vehicle_observation import SyntheticVehicleObservation

OPEN_SECONDS = 9 * 3600  # 09:00:00
CLOSE_SECONDS = 19 * 3600 - 1  # 18:59:59
MIN_VISIT_SECONDS = 10 * 60  # shortest realistic gap between entry and exit
SUNDAY = 6  # date.weekday()

MUNICIPALITIES_PATH = Path('/app/shared-data/municipalities.json')

VEHICLE_TYPES = ['car', 'suv', 'van', 'truck', 'motorcycle', 'bus']

MAKE_MODELS = [
    ('Toyota', 'Corolla'),
    ('Toyota', 'RAV4'),
    ('Volkswagen', 'Golf'),
    ('Volkswagen', 'Passat'),
    ('Skoda', 'Octavia'),
    ('Skoda', 'Fabia'),
    ('BMW', '3 Series'),
    ('BMW', 'X5'),
    ('Mercedes-Benz', 'C-Class'),
    ('Mercedes-Benz', 'Sprinter'),
    ('Audi', 'A4'),
    ('Audi', 'Q5'),
    ('Ford', 'Focus'),
    ('Ford', 'Transit'),
    ('Opel', 'Astra'),
    ('Renault', 'Clio'),
]

COLORS = ['white', 'black', 'grey', 'silver', 'blue', 'red', 'green']

# Matches the regions the real Plate Recognizer call is restricted to (see
# PlateRecognizerHandler.send_to_api), weighted toward Austrian traffic.
COUNTRY_WEIGHTS = [('at', 0.75), ('de', 0.09), ('si', 0.10), ('hu', 0.06)]


def load_municipality_codes() -> dict[str, list[str]]:
    """Loads Austrian and Slovenian municipality codes, keyed by country code."""
    if not MUNICIPALITIES_PATH.exists():
        return {'at': [], 'si': []}

    with MUNICIPALITIES_PATH.open(encoding='utf-8') as f:
        data = json.load(f)

    at_codes = [code for group in data.get('Austria', {}).values() for entry in group for code in entry]
    si_codes = [code for entry in data.get('Slovenia', {}).get('Municipalities', []) for code in entry]

    return {'at': at_codes, 'si': si_codes}


def weighted_country_code() -> str:
    values, weights = zip(*COUNTRY_WEIGHTS)
    return random.choices(values, weights=weights, k=1)[0]


def random_plate(country_code: str, municipality_codes: dict[str, list[str]]) -> tuple[str, str | None]:
    """Builds a plate string in a style resembling the given country's plates.

    Returns the plate text along with the municipality code used, if any.
    """
    codes = municipality_codes.get(country_code, [])
    municipality = random.choice(codes) if codes else None

    digits = random.randint(1, 9999)
    letters = ''.join(random.choices(string.ascii_uppercase, k=random.randint(1, 2)))
    prefix = municipality or country_code.upper()

    return f'{prefix}-{digits}{letters}', municipality


def hash_plate(plate: str) -> bytes:
    return sha256(plate.strip().lower().encode('utf-8')).digest()


def workdays_between(start: date, end: date):
    """Yields each date in [start, end] that isn't a Sunday."""
    current = start
    while current <= end:
        if current.weekday() != SUNDAY:
            yield current
        current += timedelta(days=1)


def random_visit_times(day: date) -> tuple[datetime, datetime]:
    """Picks an entry and exit time for one day, both within business hours."""
    entry_seconds = random.randint(OPEN_SECONDS, CLOSE_SECONDS - MIN_VISIT_SECONDS)
    exit_seconds = random.randint(entry_seconds + MIN_VISIT_SECONDS, CLOSE_SECONDS)

    midnight = datetime.combine(day, time())
    return midnight + timedelta(seconds=entry_seconds), midnight + timedelta(seconds=exit_seconds)


def build_visit(
    day: date, plate: str, country_code: str, municipality: str | None
) -> list[SyntheticVehicleObservation]:
    """Builds one entry + one exit observation for a single plate on a single day."""
    entry_time, exit_time = random_visit_times(day)

    make, model = random.choice(MAKE_MODELS)
    shared_kwargs = {
        'plate_hash': hash_plate(plate),
        'country_code': country_code,
        'municipality': municipality,
        'vehicle_type': random.choice(VEHICLE_TYPES),
        'make': make,
        'model': model,
        'color': random.choice(COLORS),
    }

    entry = SyntheticVehicleObservation(
        **shared_kwargs,
        plate_score=random.randint(750, 999),
        orientation=VehicleOrientation.FRONT,
        timestamp=entry_time,
    )
    exit_ = SyntheticVehicleObservation(
        **shared_kwargs,
        plate_score=random.randint(750, 999),
        orientation=VehicleOrientation.REAR,
        timestamp=exit_time,
    )
    return [entry, exit_]


def generate(num_plates: int, weeks: int) -> list[SyntheticVehicleObservation]:
    municipality_codes = load_municipality_codes()

    plates = []
    for _ in range(num_plates):
        country_code = weighted_country_code()
        plate, municipality = random_plate(country_code, municipality_codes)
        plates.append((plate, country_code, municipality))

    end = date.today()
    start = end - timedelta(weeks=weeks)

    observations: list[SyntheticVehicleObservation] = []
    for day in workdays_between(start, end):
        for plate, country_code, municipality in plates:
            observations.extend(build_visit(day, plate, country_code, municipality))

    return observations


def get_engine():
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    db_name = os.environ['DB_NAME']

    url = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    return create_engine(url)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--plates', type=int, default=25, help='Number of distinct license plates to simulate.')
    parser.add_argument('--weeks', type=int, default=4, help='How many weeks back from today to generate data for.')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducible output.')
    parser.add_argument(
        '--clear', action='store_true', help='Delete existing synthetic data before generating new rows.'
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    observations = generate(args.plates, args.weeks)

    engine = get_engine()
    with Session(engine) as session:
        if args.clear:
            session.query(SyntheticVehicleObservation).delete()
        session.add_all(observations)
        session.commit()

    print(
        f'Inserted {len(observations)} synthetic observations '
        f'({args.plates} plates, visiting every Mon-Sat over the last {args.weeks} weeks).'
    )


if __name__ == '__main__':
    main()
