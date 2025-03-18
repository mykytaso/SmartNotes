import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from database import (
    reset_sqlite_database,
    get_db_contextmanager,
    NoteModel,
)
from main import app


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db():
    """
    Reset the SQLite database before each test.

    This fixture ensures that the database is cleared and recreated for every test function.
    It helps maintain test isolation by preventing data leakage between tests.
    """
    await reset_sqlite_database()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provide an asynchronous test client for making HTTP requests."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Provide an async database session for database interactions.

    This fixture yields an async session using `get_db_contextmanager`, ensuring that the session
    is properly closed after each test.
    """
    async with get_db_contextmanager() as session:
        yield session


@pytest.fixture
async def populate_test_10_notes(db_session):

    notes = [NoteModel(content=f"Content {i}") for i in range(1, 11)]
    db_session.add_all(notes)

    await db_session.flush()
    await db_session.commit()
    yield
