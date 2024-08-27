from datetime import datetime, timezone
from uuid import UUID, uuid4
from beanie import Document, Indexed
from pydantic import Field


class Post(Document):
    id: UUID = Field(default_factory=uuid4)
    subject: Indexed(str, unique=False)
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
