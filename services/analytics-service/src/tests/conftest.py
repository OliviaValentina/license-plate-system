from dataclasses import dataclass, field
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Table, create_engine, delete, insert
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings
from src.db.session import get_db
from src.main import app

test_engine = create_engine(str(settings.db_uri))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# analytics_user only has SELECT on ingestion_schema (see db/init.sql), so tests that
# need to seed ingestion rows use a superuser connection instead - the same credentials
# db-prestart already uses to run init.sql/migrations.
_admin_uri = (
    f'postgresql+psycopg2://{os.environ["POSTGRES_ADMIN_USER"]}:{os.environ["POSTGRES_ADMIN_PASSWORD"]}'
    f'@{settings.db_host}:{settings.db_port}/{settings.db_name}'
)
admin_engine = create_engine(_admin_uri)
AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)


@dataclass
class AdminDb:
    """Wraps a superuser session for seeding ingestion rows in tests.

    Rows are committed for real (not just at the ORM session level), since the `db`
    fixture used to read them back is a *separate* connection authenticated as
    analytics_user - under READ COMMITTED isolation it cannot see writes still sitting
    in another connection's open transaction. Each inserted row is tracked and deleted
    again at teardown, so tests stay isolated without relying on transaction rollback.
    """

    session: Session
    _inserted: list[tuple[Table, int]] = field(default_factory=list)

    def insert_observation(self, table: Table, **values) -> int:
        result = self.session.execute(insert(table).values(**values))
        self.session.commit()
        inserted_id = result.inserted_primary_key[0]
        self._inserted.append((table, inserted_id))
        return inserted_id

    def _cleanup(self) -> None:
        for table, row_id in self._inserted:
            self.session.execute(delete(table).where(table.c.id == row_id))
        self.session.commit()


@pytest.fixture(scope='function')
def db():
    """
    Provides a SQLAlchemy session (as analytics_user) for each test function.
    Each test will run within its own transaction, which is then rolled back
    at the end of the test, ensuring data isolation without dropping tables.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def admin_db():
    """
    Provides an AdminDb helper (superuser privileges) for seeding rows directly in
    ingestion_schema, since analytics_user has no INSERT grant there. See AdminDb for
    why this can't use the same rollback-based isolation as the `db` fixture.
    """
    session = AdminSessionLocal()
    wrapper = AdminDb(session=session)

    try:
        yield wrapper
    finally:
        wrapper._cleanup()
        session.close()


@pytest.fixture(scope='function')
def client(db):
    """
    Provides a FastAPI test client configured to use the `db` fixture's session.
    """

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        # Clear overrides to ensure subsequent tests don't use this override
        app.dependency_overrides.clear()
