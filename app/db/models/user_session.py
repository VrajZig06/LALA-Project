from sqlalchemy.orm import relationship
from sqlalchemy import String, Boolean, ForeignKey
from app.db.models.base import IdMixins, TimeMixins
from sqlalchemy.orm import Mapped, mapped_column

class UserSession(IdMixins, TimeMixins):
    __tablename__ = "user_sessions"

    # Table fields
    session: Mapped[str] = mapped_column(String)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates = "user_sessions") # One to One