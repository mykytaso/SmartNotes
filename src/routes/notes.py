from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db, NoteModel
from schemas import NoteVersionListResponseSchema
from schemas.notes import (
    NoteListResponseSchema,
    NoteDetailResponseSchema,
    NoteRequestCreateSchema,
    NoteRequestUpdateSchema,
)

router = APIRouter()


@router.get("/notes/", response_model=NoteListResponseSchema)
async def get_notes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
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


@router.get("/notes/{note_id}/", response_model=NoteDetailResponseSchema)
async def get_note(note_id: int, db: AsyncSession = Depends(get_db)):
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


@router.post("/notes/", response_model=NoteRequestCreateSchema)
async def create_note(note_data: NoteRequestCreateSchema, db: AsyncSession = Depends(get_db)):
    note = NoteModel(**note_data.model_dump())
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.get("/notes/{note_id}/versions/", response_model=NoteVersionListResponseSchema)
async def get_note_versions(
    note_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    note = await get_note(note_id, db)

    versions = note.versions
    total_versions = len(versions)
    total_pages = (total_versions + per_page - 1) // per_page

    offset = (page - 1) * per_page
    paginated_versions = versions[offset : offset + per_page]

    return {
        "versions": paginated_versions,
        "prev_page": (
            f"/notes/{note_id}/versions/?page={page - 1}&per_page={per_page}"
            if page > 1
            else None
        ),
        "next_page": (
            f"/notes/{note_id}/versions/?page={page + 1}&per_page={per_page}"
            if page < total_pages
            else None
        ),
        "total_pages": total_pages,
        "total_items": total_versions,
    }
