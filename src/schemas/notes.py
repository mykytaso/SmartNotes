from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BaseModelPaginated(BaseModel):
    """Base schema for paginated responses."""

    prev_page: Optional[str] = Field(None, description="URL for previous page")
    next_page: Optional[str] = Field(None, description="URL for next page")
    total_pages: int = Field(..., description="Total number of pages")
    total_items: int = Field(..., description="Total number of notes")


class NoteDetailResponseSchema(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    versions: List["VersionDetailResponseSchema"]


class NoteListResponseSchema(BaseModelPaginated):
    notes: List[NoteDetailResponseSchema]


class NoteCreateRequestSchema(BaseModel):
    content: str = Field(..., description="The content of the note")


class NoteUpdateRequestSchema(BaseModel):
    content: str = Field(..., description="The updated content of the note")


class VersionDetailResponseSchema(BaseModel):
    id: int
    note_id: int
    version: int
    content: str
    created_at: datetime


class VersionListResponseSchema(BaseModelPaginated):
    versions: List[VersionDetailResponseSchema]
