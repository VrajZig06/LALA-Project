from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.core.enums import RazorpayPeriodCycles, RazorpayCurrency

# Subscription Plan Create
class SubscriptionPlanCreate(BaseModel):
    name: str
    description: str
    price: float
    period: RazorpayPeriodCycles
    interval: int
    currency: RazorpayCurrency
    duration: int

# Subscription Plan Response
class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    period: RazorpayPeriodCycles
    interval: int
    currency: RazorpayCurrency
    razorpay_plan_id: str
    duration: int

    model_config = ConfigDict(from_attributes=True)