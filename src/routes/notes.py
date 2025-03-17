from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db, NoteModel, VersionModel
from schemas import (
    NoteListResponseSchema,
    NoteDetailResponseSchema,
    NoteCreateRequestSchema,
    NoteUpdateRequestSchema,
)

router = APIRouter()


@router.get("/", response_model=NoteListResponseSchema)
async def get_note_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a paginated list of notes with their versions.
    Returns a list of notes with pagination metadata.
    """
    offset = (page - 1) * per_page

    result = await db.execute(
        select(NoteModel)
        .options(selectinload(NoteModel.versions))
        .offset(offset)
        .limit(per_page)
    )
    notes = result.scalars().all()

    if not notes:
        return {
            "notes": [],
            "prev_page": None,
            "next_page": None,
            "total_pages": 0,
            "total_items": 0,
        }

    total_notes = await db.scalar(select(func.count(NoteModel.id)))
    total_pages = (total_notes + per_page - 1) // per_page

    return {
        "notes": notes,
        "prev_page": (
            f"/notes/?page={page - 1}&per_page={per_page}" if page > 1 else None
        ),
        "next_page": (
            f"/notes/?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        "total_pages": total_pages,
        "total_items": total_notes,
    }


@router.get("{note_id}/", response_model=NoteDetailResponseSchema)
async def retrieve_note(note_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single note by ID.
    Returns the note with the given ID.
    """
    result = await db.execute(
        select(NoteModel)
        .where(NoteModel.id == note_id)
        .options(selectinload(NoteModel.versions))
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=404, detail="Note with the given ID was not found."
        )
    return note


@router.post("/", response_model=NoteDetailResponseSchema)
async def create_note(
    note_data: NoteCreateRequestSchema, db: AsyncSession = Depends(get_db)
):
    """
    Create a new note.
    Returns the newly created note.
    """
    note = NoteModel(**note_data.model_dump())
    db.add(note)
    await db.commit()

    # Refresh with explicit relationship loading
    result = await db.execute(
        select(NoteModel)
        .where(NoteModel.id == note.id)
        .options(selectinload(NoteModel.versions))
    )
    return result.scalar_one()


@router.put("/{note_id}", response_model=NoteDetailResponseSchema)
async def update_note(
    note_id: int, note_data: NoteUpdateRequestSchema, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing note by ID.
    Creates a new version with the previous note content and updates the note with new content.
    Returns the updated note with its versions.
    """
    note = await retrieve_note(note_id, db)

    # Check the latest version of the note
    latest_version_result = await db.execute(
        select(func.max(VersionModel.version)).where(VersionModel.note_id == note_id)
    )
    latest_version = latest_version_result.scalar() or 0

    # Store the version of the note
    version = VersionModel(
        note_id=note_id,
        content=note.content,
        version=latest_version + 1,
        created_at=note.updated_at,
    )

    # Update the note content and updated_at
    note.content = note_data.content
    note.updated_at = datetime.now(tz=UTC)

    db.add(version)
    await db.commit()
    await db.refresh(note)

    return note


@router.delete("/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a note by ID.
    """
    note = await retrieve_note(note_id, db)

    await db.delete(note)
    await db.commit()
    return {"message": "Note deleted successfully."}
