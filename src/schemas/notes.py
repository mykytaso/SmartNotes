from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from schemas import NoteVersionListResponseSchema


class NoteDetailResponseSchema(BaseModel):
    id: int
    content: str
    created_at: datetime
    updated_at: datetime
    versions: List["NoteVersionListResponseSchema"]


class NoteListResponseSchema(BaseModel):
    notes: List[NoteDetailResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int
