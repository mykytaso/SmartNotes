from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from schemas import NoteVersionListResponseSchema


class NoteDetailResponseSchema(BaseModel):
    """Schema for note detail response."""

    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    versions: List["NoteVersionListResponseSchema"]


class NoteListResponseSchema(BaseModel):
    """Schema for paginated note list response."""

    notes: List[NoteDetailResponseSchema]
    prev_page: Optional[str] = Field(None, description="URL for previous page")
    next_page: Optional[str] = Field(None, description="URL for next page")
    total_pages: int = Field(..., description="Total number of pages")
    total_items: int = Field(..., description="Total number of notes")


class NoteRequestCreateSchema(BaseModel):
    """Schema for creating a new note."""

    content: str = Field(..., description="The content of the note")


class NoteRequestUpdateSchema(BaseModel):
    """Schema for updating an existing note."""

    content: str = Field(..., description="The updated content of the note")
