import random
import pytest
from sqlalchemy import select, func

from database import NoteModel, VersionModel


random_id = random.randint(1, 1000)


@pytest.mark.asyncio
async def test_get_versions_empty_database(client):
    """
    Test retrieving versions from an empty database.

    Expected:
        - 200 response status code.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """

    response = await client.get(f"/api/v1/versions/{random_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Note with the given ID was not found."}



@pytest.mark.asyncio
async def test_get_versions_default_parameters(client, populate_test_notes):
    """
    Test retrieving versions with default pagination parameters.

    Expected:
        - 200 response status code.
        - 10 versions returned.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """
    response = await client.get(f"/api/v1/versions/{random_id}")
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data["versions"]) == 10
    assert response_data["total_pages"] > 0
    assert response_data["total_items"] > 0
    assert response_data["prev_page"] is None
    if response_data["total_pages"] > 1:
        assert response_data["next_page"] is not None