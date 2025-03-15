from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, NoteModel
from schemas.notes import NoteListResponseSchema, NoteDetailResponseSchema

router = APIRouter()


@router.get("/notes/", response_model=NoteListResponseSchema)
async def get_notes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page
    stmt = select(NoteModel).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    notes = result.scalars().all()

    if not notes:
        raise HTTPException(status_code=404, detail="No notes found.")

    total_notes = await db.scalar(select(func.count(NoteModel.id)))
    total_pages = (total_notes + per_page - 1) // per_page
    if not total_notes:
        raise HTTPException(status_code=404, detail="No notes found.")

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


@router.get("/notes/{note_id}/", response_model=NoteDetailResponseSchema)
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NoteModel).where(NoteModel.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=404, detail="Note with the given ID was not found."
        )
    return note


@router.get("/notes/{note_id}/versions/", response_model=NoteDetailResponseSchema)
async def get_note_versions(note_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NoteModel).where(NoteModel.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(
            status_code=404, detail="Note with the given ID was not found."
        )
    return note.versions
