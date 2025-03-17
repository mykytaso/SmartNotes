from fastapi import Depends, APIRouter
from sqlalchemy import select, func, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, NoteModel
from routes.notes import retrieve_note
from services import get_common_words_phrases, genai_summarize

router = APIRouter()


@router.get("/{note_id}/summary")
async def get_note_summary(
    note_id: int, max_words: int = 10, db: AsyncSession = Depends(get_db)
):
    """
    Generate a summary of a note by ID with a maximum number of words using the GenAI API.

    Args:
        note_id (int): The ID of the note to summarize.
        max_words (int): The maximum number of words in the summary (default: 10).
        db (AsyncSession): Database session dependency.

    Returns:
        The summary of the note.
    """
    note = await retrieve_note(note_id, db)
    summary = await genai_summarize(note.content, max_words)

    return {"summary": summary}


@router.get("/total-words")
async def get_total_words(db: AsyncSession = Depends(get_db)):
    """
    Retrieve the total word count from all notes in the database using SQLAlchemy.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        The total word count of all notes in the database.
    """
    statement = select(
        func.sum(
            func.length(NoteModel.content)
            - func.length(func.replace(NoteModel.content, " ", ""))
            + 1
        )
    )
    result = await db.execute(statement)
    total_words = result.scalar() or 0

    return {"total_words": total_words}


@router.get("/avg-note-length")
async def get_avg_note_length(db: AsyncSession = Depends(get_db)):
    """
    Calculate the average note length across all notes in the database.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        The average note length rounded to 2 decimal places.
    """
    statement = select(
        func.sum(func.length(NoteModel.content)) / cast(func.count(NoteModel.id), Float)
    )
    result = await db.execute(statement)

    avg_note_length = result.scalar()
    avg_note_length_rounded = round(avg_note_length, 2) if avg_note_length else 0

    return {"avg_note_length": avg_note_length_rounded}


@router.get("/most-common-words-or-phrases")
async def get_most_common_words_or_phrases(
    max_phrase_length: int = 3, db: AsyncSession = Depends(get_db)
):
    """
    Extract the most common words or phrases from all notes in the database.

    Args:
        max_phrase_length (int): The maximum length of phrases to consider, ranging from 1 to 10 words (default: 3 words).
        db (AsyncSession): Database session dependency.

    Returns:
        Common words or phrases (up to 'max_phrase_length' words) that appear at least twice, and their frequencies.
    """

    # Ensure max_phrase_length is between 1 and 10
    max_phrase_length = min(max(1, max_phrase_length), 10)

    result = await db.execute(select(NoteModel.content))
    notes = result.scalars().all()

    result = await get_common_words_phrases(notes, max_phrase_length)

    return result


@router.get("/top3-longest-notes")
async def get_top3_longest_notes(db: AsyncSession = Depends(get_db)):
    """
    Retrieve the top 3 longest notes in the database.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        The top 3 longest notes.
    """
    statement = (
        select(NoteModel).order_by(func.length(NoteModel.content).desc()).limit(3)
    )
    result = await db.execute(statement)
    notes = result.scalars().all()

    # Add length information to each note
    notes_with_length = [
        {
            "id": note.id,
            "length": len(note.content),
            "content": note.content,
        }
        for note in notes
    ]

    return {"top3_longest_notes": notes_with_length}


@router.get("/top3-shortest-notes")
async def get_top3_shortest_notes(db: AsyncSession = Depends(get_db)):
    """
    Retrieve the top 3 shortest notes in the database.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        The top 3 shortest notes.
    """
    statement = select(NoteModel).order_by(func.length(NoteModel.content)).limit(3)
    result = await db.execute(statement)
    notes = result.scalars().all()

    # Add length information to each note
    notes_with_length = [
        {
            "id": note.id,
            "length": len(note.content),
            "content": note.content,
        }
        for note in notes
    ]

    return {"top3_shortest_notes": notes_with_length}
