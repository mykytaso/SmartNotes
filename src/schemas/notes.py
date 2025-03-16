from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from schemas import VersionDetailResponseSchema


class NoteDetailResponseSchema(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    versions: List["VersionDetailResponseSchema"]


class NoteListResponseSchema(BaseModel):
    notes: List[NoteDetailResponseSchema]

    prev_page: Optional[str] = Field(None, description="URL for previous page")
    next_page: Optional[str] = Field(None, description="URL for next page")
    total_pages: int = Field(..., description="Total number of pages")
    total_items: int = Field(..., description="Total number of notes")


class NoteCreateRequestSchema(BaseModel):
    content: str = Field(..., description="The content of the note")


class NoteUpdateRequestSchema(BaseModel):
    content: str = Field(..., description="The updated content of the note")
