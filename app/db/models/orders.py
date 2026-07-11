from sqlalchemy import Float
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy import Enum as SEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import LoginType
from app.db.models.base import IdMixins, TimeMixins


class Order(IdMixins, TimeMixins):
    __tablename__ = "orders"

    razorpay_order_id: Mapped[str] = mapped_column(String, nullable = False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float,CheckConstraint('price > 0.0'), nullable = False)


    # Relationships
    user = relationship("User", back_populates = "order")    
    order_item = relationship("OrderItem", back_populates = "order")