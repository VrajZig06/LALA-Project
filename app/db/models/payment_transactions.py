from sqlalchemy import Float
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy import Enum as SEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import RazorpayPaymentStatus
from app.db.models.base import IdMixins, TimeMixins


class PaymentTransaction(IdMixins, TimeMixins):
    __tablename__ = "payment_transactions"

    payment_id: Mapped[str] = mapped_column(String, nullable = False)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    status: Mapped[str] = mapped_column(SEnum(RazorpayPaymentStatus), nullable=True, default=RazorpayPaymentStatus.PENDING.value)


    # Relationships
    order = relationship("Order", back_populates = "payment_transaction")