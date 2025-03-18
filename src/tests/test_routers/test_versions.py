import random

import pytest
from sqlalchemy import select, func

from database import NoteModel, VersionModel

random_id = random.randint(1, 10)


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
async def test_get_10_note_versions_default_parameters(client, populate_test_10_notes):
    """
    Test updating a note 10 times and retrieving 10 versions with default pagination parameters.

    Expected:
        - 200 response status code.
        - 10 versions returned.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """

    for n in range(1, 11):
        await client.put(
            f"/api/v1/notes/{random_id}/", json={"content": f"Updated Content {n}"}
        )

    response = await client.get(f"/api/v1/versions/{random_id}")
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data["versions"]) == 10
    assert response_data["total_pages"] > 0
    assert response_data["total_items"] > 0
    assert response_data["prev_page"] is None
    if response_data["total_pages"] > 1:
        assert response_data["next_page"] is not None


@pytest.mark.asyncio
async def test_get_note_version_by_note_id_version_id_not_found(
    client, populate_test_10_notes
):
    """
    Test retrieving a version that does not exist because note was not updated.

    Expected:
        - 200 response status code.
        - 10 versions returned.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """

    response = await client.get(f"/api/v1/versions/{random_id}/{random_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Version with the given ID was not found."}


@pytest.mark.asyncio
async def test_get_note_version_by_note_id_version_id(client, populate_test_10_notes):
    """
    Test updating a note 10 times and retrieving 10 versions with default pagination parameters.

    Expected:
        - 200 response status code.
        - 10 versions returned.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """
    for n in range(1, 11):
        await client.put(
            f"/api/v1/notes/{random_id}/", json={"content": f"Updated Content {n}"}
        )

    response = await client.get(f"/api/v1/versions/{random_id}/{random_id}")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == random_id
    assert response_data["content"] == f"Updated Content {random_id - 1}"


@pytest.mark.asyncio
async def test_delete_version(client, db_session, populate_test_10_notes):
    """
    Test delete a note version by note ID and version ID.

    Expected:
        - 200 response status code.
        - JSON response with a "Version deleted successfully." message.
    """

    for n in range(1, 11):
        await client.put(
            f"/api/v1/notes/{random_id}/", json={"content": f"Updated Content {n}"}
        )

    total_versions = await db_session.scalar(
        select(func.count())
        .select_from(VersionModel)
        .where(VersionModel.note_id == random_id)
    )

    assert total_versions == 10

    response_delete = await client.delete(f"/api/v1/versions/{random_id}/{random_id}")

    assert response_delete.status_code == 200
    assert response_delete.json() == {"message": "Version deleted successfully."}

    number_of_versions_after_delete = await db_session.scalar(
        select(func.count())
        .select_from(VersionModel)
        .where(VersionModel.note_id == random_id)
    )

    assert number_of_versions_after_delete == total_versions - 1
