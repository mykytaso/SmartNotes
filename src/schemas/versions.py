from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VersionDetailResponseSchema(BaseModel):
    id: int
    note_id: int
    version: int
    content: str
    created_at: datetime


class VersionListResponseSchema(BaseModel):
    versions: List[VersionDetailResponseSchema]

    prev_page: Optional[str] = Field(None, description="URL for previous page")
    next_page: Optional[str] = Field(None, description="URL for next page")
    total_pages: int = Field(..., description="Total number of pages")
    total_items: int = Field(..., description="Total number of notes")
