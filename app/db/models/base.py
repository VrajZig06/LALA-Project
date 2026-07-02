from app.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, BigInteger, Boolean
from app.common.utils import get_unix_time
import uuid


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
