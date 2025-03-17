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
    Generate a summary of a note by ID with a maximum number of words.
    Returns the summary of the note.
    """
    note = await retrieve_note(note_id, db)
    summary = await genai_summarize(note.content, max_words)

    return {"summary": summary}


@router.get("/total-words-count")
async def get_total_word_count(db: AsyncSession = Depends(get_db)):
    """
    Calculate the total word count across all notes in the database using SQLAlchemy.
    """
    statement = select(
        func.sum(
            func.length(NoteModel.content)
            - func.length(func.replace(NoteModel.content, " ", ""))
            + 1
        )
    )
    result = await db.execute(statement)
    total_word_count = result.scalar()

    return total_word_count or 0


@router.get("/avg-note-length")
async def get_avg_note_length(db: AsyncSession = Depends(get_db)):
    """
    Calculate the average note length across all notes in the database.
    """
    statement = select(
        func.sum(func.length(NoteModel.content)) / cast(func.count(NoteModel.id), Float)
    )
    result = await db.execute(statement)
    avg_note_length = result.scalar()

    return round(avg_note_length, 2) if avg_note_length else 0


@router.get("/most-common-words-or-phrases")
async def get_most_common_words_or_phrases(
    max_phrase_length: int = 3, db: AsyncSession = Depends(get_db)
):
    """
    Calculate the most common words or phrases across all notes in the database.
    Args:
        max_phrase_length (int): The maximum length of the phrases to consider.
        db (AsyncSession): The database connection.
    Returns:
        (dict): A dictionary where the keys are the most common words or phrases (with a length
        up to 'max_phrase_length') that appear at least twice, and the values are the
        frequencies (count) of those words/phrases.
    """
    result = await db.execute(select(NoteModel.content))
    notes = result.scalars().all()
    result = await get_common_words_phrases(notes, max_phrase_length)
    return result
