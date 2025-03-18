import random
import pytest
from sqlalchemy import select, func

from database import NoteModel


random_id = random.randint(1, 10)


@pytest.mark.asyncio
async def test_get_notes_empty_database(client):
    """
    Test retrieving notes from an empty database.

    Expected:
        - 200 response status code.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """
    response = await client.get("/api/v1/notes/")

    assert response.status_code == 200
    assert response.json() == {
        "next_page": None,
        "notes": [],
        "prev_page": None,
        "total_items": 0,
        "total_pages": 0,
    }


@pytest.mark.asyncio
async def test_get_notes_default_parameters(client, populate_test_10_notes):
    """
    Test retrieving notes with default pagination parameters.

    Expected:
        - 200 response status code.
        - 10 notes returned.
        - Pagination metadata (`total_pages`, `total_items`, `prev_page`, `next_page`).
    """
    response = await client.get("/api/v1/notes/")
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data["notes"]) == 10
    assert response_data["total_pages"] > 0
    assert response_data["total_items"] > 0
    assert response_data["prev_page"] is None
    if response_data["total_pages"] > 1:
        assert response_data["next_page"] is not None


@pytest.mark.asyncio
async def test_get_notes_with_custom_parameters(client, populate_test_10_notes):
    """
    Test retrieving notes with custom pagination parameters.

    Expected:
        - 200 response status code.
        - Requested number of notes (`per_page`).
        - Correct `prev_page` and `next_page` links based on pagination.
    """
    page = 1
    per_page = 5

    response = await client.get(f"/api/v1/notes/?page={page}&per_page={per_page}")
    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data["notes"]) == per_page
    assert response_data["total_pages"] > 0
    assert response_data["total_items"] > 0
    if page > 1:
        assert response_data["prev_page"] is not None
    if page < response_data["total_pages"]:
        assert response_data["next_page"] is not None
    else:
        assert response_data["next_page"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page, per_page, expected_detail",
    [
        (0, 10, "Input should be greater than or equal to 1"),
        (1, 0, "Input should be greater than or equal to 1"),
        (0, 0, "Input should be greater than or equal to 1"),
    ],
)
async def test_invalid_page_and_per_page(client, page, per_page, expected_detail):
    """
    Test invalid pagination parameters.

    Expected:
        - 422 response status code.
        - JSON validation error with the expected message.
    """
    response = await client.get(f"/api/v1/notes/?page={page}&per_page={per_page}")
    assert response.status_code == 422

    response_data = response.json()
    assert any(expected_detail in error["msg"] for error in response_data["detail"])


@pytest.mark.asyncio
async def test_per_page_maximum_allowed_value(client, populate_test_10_notes):
    """
    Test retrieving notes with the maximum allowed `per_page` value.

    Expected:
        - 200 response status code.
        - A maximum of 20 notes in the response.
    """
    response = await client.get("/api/v1/notes/?page=1&per_page=20")
    assert response.status_code == 200

    response_data = response.json()
    assert "notes" in response_data
    assert len(response_data["notes"]) <= 20


@pytest.mark.asyncio
async def test_page_exceeds_maximum(client, db_session, populate_test_10_notes):
    """
    Test retrieving a page number that exceeds the total available pages.

    Expected:
        - 200 response status code.
        - JSON response with empty list of notes.
    """
    per_page = 10
    total_notes = await db_session.scalar(select(func.count()).select_from(NoteModel))
    max_page = (total_notes + per_page - 1) // per_page

    response = await client.get(
        f"/api/v1/notes/?page={max_page + 1}&per_page={per_page}"
    )
    assert response.status_code == 200
    assert response.json()["notes"] == []


@pytest.mark.asyncio
async def test_get_note_by_id_not_found(client):
    """
    Test retrieving a note by an ID that does not exist.

    Expected:
        - 404 response status code.
        - JSON response with a "Note with the given ID was not found." error.
    """
    note_id = 1
    response = await client.get(f"/api/v1/notes/{note_id}/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Note with the given ID was not found."}


@pytest.mark.asyncio
async def test_get_note_by_id_valid(client, db_session, populate_test_10_notes):
    """
    Test retrieving a valid note by ID.

    Expected:
        - 200 response status code.
        - JSON response containing the correct note details.
    """

    expected_note = await db_session.get(NoteModel, random_id)
    assert expected_note is not None

    response = await client.get(f"/api/v1/notes/{random_id}/")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["id"] == expected_note.id
    assert response_data["content"] == expected_note.content


@pytest.mark.asyncio
async def test_update_note(client, populate_test_10_notes):
    """
    Test updating a note by ID and verify that a new note version is automatically created.

    Expected:
        - 200 response status code.
        - JSON response containing the updated note details.
        - JSON response containing the note version details.
    """
    response = await client.get(f"/api/v1/notes/1/")
    assert response.status_code == 200
    assert response.json()["content"] == "Content 1"

    response_updated = await client.put(
        f"/api/v1/notes/1/", json={"content": "Updated Content 1"}
    )
    assert response_updated.status_code == 200
    assert response_updated.json()["content"] == "Updated Content 1"
    assert (
        response_updated.json()["versions"][0]["content"] == response.json()["content"]
    )


@pytest.mark.asyncio
async def test_delete_note(client, db_session, populate_test_10_notes):
    """
    Test delete a note by ID.

    Expected:
        - 200 response status code.
        - JSON response with a "Note deleted successfully." message.
    """
    total_notes = await db_session.scalar(select(func.count()).select_from(NoteModel))

    response_delete = await client.delete(f"/api/v1/notes/{random_id}/")

    assert response_delete.status_code == 200
    assert response_delete.json() == {"message": "Note deleted successfully."}

    number_of_notes_after_delete = await db_session.scalar(
        select(func.count()).select_from(NoteModel)
    )

    assert number_of_notes_after_delete == total_notes - 1
