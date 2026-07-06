from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy import Enum as SEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LoginType
from app.db.models.base import IdMixins, TimeMixins


class User(IdMixins, TimeMixins):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String, nullable=True, default=None)
    last_name: Mapped[str] = mapped_column(String, nullable=True, default=None)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=True, default=None)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    otp: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    otp_expiry: Mapped[int] = mapped_column(BigInteger, nullable=True, default=None)
    login_type: Mapped[str] = mapped_column(
        SEnum(LoginType), nullable=True, default=LoginType.EMAIL.value
    )
    social_id: Mapped[str] = mapped_column(String, nullable=True, default=None)

    # Foreign Keys
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), nullable=False)

    # Relationships
    user_sessions: Mapped["UserSession"] = relationship(
        "UserSession", back_populates="user"
    )  # One to One
    user_info: Mapped["UserInformation"] = relationship(
        "UserInformation", back_populates="user"
    )  # One to One
    role: Mapped["Role"] = relationship("Role", back_populates="user")  # One to One
