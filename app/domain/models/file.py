import uuid

from pydantic import BaseModel, Field


class File(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    filepath: str = ""
    key: str = ""
    extension: str = ""
    mime_type: str = ""
    size: int = 0
