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
    VersionListResponseSchema,
    VersionDetailResponseSchema,
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


@router.post("/notes/", response_model=NoteDetailResponseSchema)
async def create_note(
    note_data: NoteCreateRequestSchema, db: AsyncSession = Depends(get_db)
):
    note = NoteModel(**note_data.model_dump())
    db.add(note)
    await db.commit()
    await db.refresh(note)

    # Add an empty list of versions to the note object.
    # I'm new to FastAPI (<24h experience), so this is my best approach for now.
    note.__dict__["versions"] = []

    return note


@router.put("/notes/{note_id}/", response_model=NoteDetailResponseSchema)
async def update_note(
    note_id: int, note_data: NoteUpdateRequestSchema, db: AsyncSession = Depends(get_db)
):
    note = await get_note(note_id, db)

    # Check the latest version of the note
    latest_version_result = await db.execute(
        select(func.max(VersionModel.version)).where(VersionModel.note_id == note_id)
    )
    latest_version = latest_version_result.scalar() or 0

    # Store the version of the note
    note_version = VersionModel(
        note_id=note_id, content=note.content, version=latest_version + 1
    )

    # Update the note content
    note.content = note_data.content

    # Save both changes (note and its version) in a single transaction
    db.add(note_version)
    await db.commit()
    await db.refresh(note)

    return note


@router.delete("/notes/{note_id}/")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await get_note(note_id, db)

    await db.delete(note)
    await db.commit()
    return {"message": "Note deleted successfully."}


@router.get("/notes/{note_id}/versions/", response_model=VersionListResponseSchema)
async def get_versions(
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


@router.get(
    "/notes/{note_id}/versions/{version_id}", response_model=VersionDetailResponseSchema
)
async def get_version(
    note_id: int, version_id: int, db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(VersionModel)
        .where(VersionModel.note_id == note_id)
        .where(VersionModel.version == version_id)
    )

    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(
            status_code=404, detail="Version with the given ID was not found."
        )
    return version


@router.delete("/notes/{note_id}/versions/{version_id}")
async def delete_version(
    note_id: int, version_id: int, db: AsyncSession = Depends(get_db)
):
    version = await get_version(note_id, version_id, db)

    # Update the note updated_at field because its version was deleted
    note = await get_note(note_id, db)
    note.updated_at = datetime.now(tz=UTC)

    db.add(note)
    await db.delete(version)
    await db.commit()
    return {"message": "Version deleted successfully."}
