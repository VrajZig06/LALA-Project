from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import IdMixins, TimeMixins


class User(IdMixins, TimeMixins):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String)
