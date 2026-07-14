from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.dependecy import RoleCheck
from app.core.logger import get_logger
from app.db.session import get_db
from app.schema.subscription import SubscriptionPlanCreate, SubscriptionCreate, CancelSubscription
from app.services.subscription_service import SubscriptionService
from app.core.dependecy import current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/subscription", tags=["Subscriptions"])

@router.post("/create-plan", summary = "Create New Subscription Plan")
async def create_subscription_plan(payload: SubscriptionPlanCreate, request: Request, current_user = Depends(RoleCheck(["admin"])), db: Session = Depends(get_db)):
    # Subscription service
    subscription_service = SubscriptionService(db)
    return subscription_service.create_subscription_plan(payload)

@router.get("/all", summary = "Get All Subscription Plans")
async def get_all_subscription_plans(
    current_user = Depends(current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db)
):
    # Subscription service
    subscription_service = SubscriptionService(db)
    return subscription_service.get_all_subscription_plans(page=page, page_size=page_size)

@router.post("/create-subscription", summary = "Create Subscription for user")
async def create_subscription(
    payload: SubscriptionCreate,
    current_user = Depends(current_user),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.create_subbscription(payload, current_user)


@router.post("/cancel-subscription", summary = "Create Subscription for user")
async def cancel_subscription(
    payload: CancelSubscription,
    current_user = Depends(current_user),
    db: Session = Depends(get_db)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.cancel_subscription(payload, current_user)