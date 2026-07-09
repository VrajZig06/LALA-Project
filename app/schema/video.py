from typing import Optional
from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    name: Optional[str] = None


class RoomResponse(BaseModel):
    id: str
    room_code: str
    name: Optional[str] = None
    host_id: str
    is_active: bool
    created_at: int
    updated_at: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
