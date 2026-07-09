from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import IdMixins, TimeMixins


class CallRoom(IdMixins, TimeMixins):
    __tablename__ = "call_rooms"

    room_code: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True, default=None)
    host_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    host: Mapped["User"] = relationship("User")
