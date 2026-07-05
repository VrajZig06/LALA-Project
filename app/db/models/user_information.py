from sqlalchemy.orm import relationship
from sqlalchemy import String, Boolean, ForeignKey
from app.db.models.base import IdMixins, TimeMixins
from sqlalchemy.orm import Mapped, mapped_column


class UserInformation(IdMixins, TimeMixins):
    __tablename__ = "user_information"

    # Table fields
    phone: Mapped[str] = mapped_column(String, nullable = False)
    country_code: Mapped[str] = mapped_column(String, nullable = False)
    address_line1: Mapped[str] = mapped_column(String, nullable = False)
    address_line2: Mapped[str] = mapped_column(String, nullable = False)
    city: Mapped[str] = mapped_column(String, nullable = False)
    state: Mapped[str] = mapped_column(String, nullable = False)
    postal_code: Mapped[str] = mapped_column(String, nullable = False)
    country: Mapped[str] = mapped_column(String, nullable = False)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates = "user_info") # One to One
