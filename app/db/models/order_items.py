from sqlalchemy import Float
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy import Enum as SEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LoginType
from app.db.models.base import IdMixins, TimeMixins


class OrderItem(IdMixins, TimeMixins):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable = False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    item_price: Mapped[float] = mapped_column(Float,CheckConstraint('item_price > 0.0'), nullable = False)
    item_quantity: Mapped[int] = mapped_column(Integer, nullable = False, default = 1)

    # Relationship
    order = relationship("Order", back_populates = 'order_item')
    user = relationship("User", back_populates = "order_item")  