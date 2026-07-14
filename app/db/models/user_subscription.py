from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import IdMixins, TimeMixins


class Subscription(IdMixins, TimeMixins):
    __tablename__ = "subscriptions"

    # Table fields
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[str] = mapped_column(
        String, ForeignKey("subscription_plans.id"), nullable=True
    )
    razorpay_subscription_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="created", server_default="created"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=True, default=1, server_default="1"
    )
    cancel_at_cycle_end: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=False, server_default="false"
    )
    current_period_start: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )
    current_period_end: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )
    ended_at: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="subscriptions")
    invoices: Mapped[list["Invoice"]] = relationship(
        "Invoice", back_populates="subscription", cascade="all, delete-orphan"
    )




