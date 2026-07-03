from sqlalchemy.orm import relationship
from sqlalchemy import Boolean
from sqlalchemy.engine import default
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import IdMixins, TimeMixins


class User(IdMixins, TimeMixins):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String, nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(String, nullable=True, default=None)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # Relationships 
    user_sessions: Mapped["UserSession"] = relationship("UserSession", back_populates = "user") # One to One
    user_info: Mapped["UserInformation"] = relationship("UserInformation", back_populates = "user") # One to One