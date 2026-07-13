from sqlalchemy import Boolean, Integer, Float
from sqlalchemy import ForeignKey, String, Enum as SEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.enums import RazorpayPeriodCycles, RazorpayCurrency

from app.db.models.base import IdMixins, TimeMixins


class SubscriptionPlan(IdMixins, TimeMixins):
    __tablename__ = "subscription_plans"

    # Table fields
    name: Mapped[str] = mapped_column(String, nullable = False)
    description: Mapped[str] = mapped_column(String, nullable = True, default = None)
    price: Mapped[float] = mapped_column(Float, nullable = False)
    razorpay_plan_id: Mapped[str] = mapped_column(String, nullable = True, default = None)
    is_recuring: Mapped[bool] = mapped_column(Boolean, nullable = True, default = False)
    period: Mapped[str] = mapped_column(SEnum(RazorpayPeriodCycles), nullable = False)
    interval: Mapped[int] = mapped_column(Integer, nullable = False)
    currency: Mapped[str] = mapped_column(
        SEnum(RazorpayCurrency), nullable = True, default = RazorpayCurrency.INR.value
    )


