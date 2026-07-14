from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.dependecy import RoleCheck
from app.core.logger import get_logger
from app.db.session import get_db
from app.schema.subscription import SubscriptionPlanCreate
from app.services.subscription_service import SubscriptionService

logger = get_logger(__name__)

router = APIRouter(prefix="/subscription", tags=["Subscriptions"])

@router.post("/create", summary = "Create New Subscription Plan")
async def create_subscription_plan(payload: SubscriptionPlanCreate, request: Request, current_user = Depends(RoleCheck(["admin"])), db: Session = Depends(get_db)):
    # Subscription service
    subscription_service = SubscriptionService(db)
    return subscription_service.create_subscription_plan(payload)

@router.get("/all", summary = "Get All Subscription Plans")
async def get_all_subscription_plans(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db)
):
    # Subscription service
    subscription_service = SubscriptionService(db)
    return subscription_service.get_all_subscription_plans(page=page, page_size=page_size)
