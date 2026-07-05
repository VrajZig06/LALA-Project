from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import IdMixins, TimeMixins

class Role(IdMixins, TimeMixins):
    __tablename__ = "roles"

    role_name: Mapped[str] = mapped_column(String, nullable = False, unique = True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates = "role")

    def __str__(self):
        return self.role_name