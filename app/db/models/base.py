import uuid

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.utils import get_unix_time
from app.db.base import Base


class IdMixins(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String, primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )


class TimeMixins(Base):
    __abstract__ = True

    # Boolean Attributes
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # Time Attributes
    created_at: Mapped[str] = mapped_column(
        BigInteger, nullable=True, default=get_unix_time
    )
    updated_at: Mapped[str] = mapped_column(
        BigInteger, nullable=True, onupdate=get_unix_time
    )
    deleted_at: Mapped[str] = mapped_column(BigInteger, nullable=True, default=None)
