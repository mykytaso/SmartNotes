from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, VersionModel
from routes.notes import retrieve_note
from schemas import (
    VersionListResponseSchema,
    VersionDetailResponseSchema,
)

router = APIRouter()


@router.get("/{note_id}", response_model=VersionListResponseSchema)
async def get_version_list(
    note_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a paginated list of versions for a note by note ID.

    Args:
        note_id (int): The ID of the note to retrieve versions for.
        page (int): The page number to retrieve (default: 1).
        per_page (int): The number of items per page (default: 10, max: 100).
        db (AsyncSession): Database session dependency.

    Returns:
        A paginated list of versions with pagination metadata.
    """
    note = await retrieve_note(note_id, db)

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
    "/{note_id}/{version_id}", response_model=VersionDetailResponseSchema
)
async def retrieve_version(
    note_id: int, version_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a version of a note by note ID and version ID.

    Args:
        note_id (int): The ID of the note to retrieve the version for.
        version_id (int): The ID of the version to retrieve.
        db (AsyncSession): Database session dependency.

    Returns:
        The version of the note.
    """

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


@router.delete("/{note_id}/{version_id}")
async def delete_version(
    note_id: int, version_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Delete a version of a note by note ID and version ID.

    Args:
        note_id (int): The ID of the note to delete the version from.
        version_id (int): The ID of the version to delete.
        db (AsyncSession): Database session dependency.

    Returns:
        A message indicating the version was deleted successfully
    """
    version = await retrieve_version(note_id, version_id, db)

    await db.delete(version)
    await db.commit()
    return {"message": "Version deleted successfully."}
