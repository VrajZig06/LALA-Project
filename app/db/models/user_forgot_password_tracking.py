from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import IdMixins, TimeMixins

class UserForgotPasswordTrack(IdMixins, TimeMixins):
    __tablename__ = "user_forgot_password_track"

    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    link_expiry: Mapped[int] = mapped_column(BigInteger, nullable = False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates = "forgot_password_liks")
