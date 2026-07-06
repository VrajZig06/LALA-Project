from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import IdMixins, TimeMixins


class UserSession(IdMixins, TimeMixins):
    __tablename__ = "user_sessions"

    # Table fields
    session: Mapped[str] = mapped_column(String)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="user_sessions"
    )  # One to One
