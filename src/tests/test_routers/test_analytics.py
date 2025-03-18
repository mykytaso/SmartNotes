import random
import pytest
from sqlalchemy import select, func, cast, Float

from database import NoteModel


random_id = random.randint(1, 10)


@pytest.mark.asyncio
async def test_summary_not_found(client):
    """
    Test summary endpoint with a note ID that does not exist in the database.

    Expected:
        - 404 response status code.
        - JSON response with a "Note with the given ID was not found." error.
    """

    response = await client.get(f"/api/v1/analytics/summary/?note_id={random_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Note with the given ID was not found."}


@pytest.mark.asyncio
async def test_summary_by_note_id(client):
    """
    Test summary endpoint with a note ID.

    Expected:
        - 200 response status code.
    """

    new_note = await client.post(
        "/api/v1/notes/", json={"content": "This is a test note."}
    )

    note_data = new_note.json()
    note_id = note_data["id"]

    response = await client.get(f"/api/v1/analytics/summary/?note_id={note_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_summary_by_note_id_and_max_words(client):
    """
    Test summary endpoint by a note ID and max_words.

    Expected:
        - 200 response status code.
        - Summary length should be less than or equal to the max_words.
    """

    new_note = await client.post(
        "/api/v1/notes/", json={"content": "This is a test note."}
    )

    note_data = new_note.json()
    note_id = note_data["id"]

    max_words = random.randint(1, 10)

    response = await client.get(
        f"/api/v1/analytics/summary/?note_id={note_id}&max_words={max_words}"
    )
    assert response.status_code == 200
    assert len(response.json()["summary"].split()) <= max_words


@pytest.mark.asyncio
async def test_total_words_no_notes(client):
    """
    Test total-words endpoint with no notes in the database.

    Expected:
        - 200 response status code.
        - JSON response with a total word count of 0.
    """

    response = await client.get("/api/v1/analytics/total-words/")

    assert response.status_code == 200
    assert response.json()["total_words"] == 0


@pytest.mark.asyncio
async def test_total_words(client, db_session, populate_test_10_notes):
    """
    Test total-words endpoint.

    Expected:
        - 200 response status code.
        - JSON response containing the total word count of all notes in the database.
    """

    total_words = await db_session.scalar(
        func.sum(
            func.length(NoteModel.content)
            - func.length(func.replace(NoteModel.content, " ", ""))
            + 1
        )
    )

    response = await client.get("/api/v1/analytics/total-words/")

    assert response.status_code == 200
    assert response.json()["total_words"] == total_words


@pytest.mark.asyncio
async def test_avg_note_length_no_notes(client):
    """
    Test avg-note-length endpoint with no notes in the database.

    Expected:
        - 200 response status code.
        - JSON response with an average note length of 0.
    """

    response = await client.get("/api/v1/analytics/avg-note-length/")

    assert response.status_code == 200
    assert response.json()["avg_note_length"] == 0


@pytest.mark.asyncio
async def test_avg_note_length(client, db_session, populate_test_10_notes):
    """
    Test avg-note-length endpoint.

    Expected:
        - 200 response status code.
        - JSON response containing the average note length across all notes in the database.
    """

    avg_note_length = await db_session.scalar(
        select(
            func.sum(func.length(NoteModel.content))
            / cast(func.count(NoteModel.id), Float)
        )
    )

    response = await client.get("/api/v1/analytics/avg-note-length/")

    assert response.status_code == 200
    assert response.json()["avg_note_length"] == avg_note_length


@pytest.mark.asyncio
async def test_get_top_3_longest_notes(
    client, populate_test_10_notes_different_length
):
    """
    Test top-3-longest-notes endpoint.

    Expected:
        - 200 response status code.
        - JSON response containing the top 3 longest notes in the database.
    """

    response = await client.get("/api/v1/analytics/top-3-longest-notes/")
    assert response.status_code == 200

    top_3_longest_notes = response.json()["top_3_longest_notes"]

    assert len(top_3_longest_notes) == 3

    for i in range(len(top_3_longest_notes) - 1):
        assert len(top_3_longest_notes[i]) >= len(top_3_longest_notes[i + 1])


@pytest.mark.asyncio
async def test_get_top3_shortest_notes(
    client, populate_test_10_notes_different_length
):
    """
    Test top-3-shortest-notes endpoint.

    Expected:
        - 200 response status code.
        - JSON response containing the top 3 shortest notes in the database.
    """

    response = await client.get("/api/v1/analytics/top-3-shortest-notes/")
    assert response.status_code == 200

    top_3_shortest_notes = response.json()["top_3_shortest_notes"]

    assert len(top_3_shortest_notes) == 3

    for i in range(len(top_3_shortest_notes) - 1):
        assert len(top_3_shortest_notes[i]) <= len(top_3_shortest_notes[i + 1])
