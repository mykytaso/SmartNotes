from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class NoteVersionDetailResponseSchema(BaseModel):
    id: int
    note_id: int
    version: int
    content: str
    created_at: datetime


class NoteVersionListResponseSchema(BaseModel):
    versions: List[NoteVersionDetailResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int
