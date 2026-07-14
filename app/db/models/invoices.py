from sqlalchemy import BigInteger, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import IdMixins, TimeMixins


class Invoice(IdMixins, TimeMixins):
    __tablename__ = "invoices"

    # Table fields
    subscription_id: Mapped[str] = mapped_column(
        String, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    razorpay_invoice_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    payment_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )
    amount: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    billing_start: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )
    billing_end: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )
    paid_at: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )

    # Relationships
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="invoices")
