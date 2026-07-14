
from fastapi import HTTPException
from fastapi import status as http_status

from app.core.config import get_settings
from app.core.exception import ServerException
from app.core.logger import get_logger
from app.core.message import ErrorMessage, SuccessMessage
from app.core.response import pagination_response, success_response
from app.db.session import Session
from app.repository.subscription_plan_repository import SubscriptionPlanRepository
from app.repository.user_repository import UserRepository
from app.schema.subscription import SubscriptionPlanCreate, SubscriptionPlanResponse
from app.services.payment_service import PaymentService

logger = get_logger(__name__)
settings = get_settings()

class SubscriptionService:
    # Constructor
    def __init__(self, db: Session):
        """
        Constructor: Takes request and DB connection object
        """
        self.db = db

        # Initialize Repository
        self.user_repo = UserRepository(db)
        self.payment_service = PaymentService(db)
        self.subscription_repo = SubscriptionPlanRepository(db)

    # Create Subscription Plan
    def create_subscription_plan(self, payload: SubscriptionPlanCreate):
        try:
            # Check if plan name exist
            subscription_name = (payload.name).lower()
            is_subscription_exist = self.subscription_repo.get_by_field("name", subscription_name)

            # If plan exist with same name raise SUBSCRIPTION_PLAN_ALREADY_EXIST
            if is_subscription_exist and is_subscription_exist.is_active and not is_subscription_exist.is_deleted:
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.SUBSCRIPTION_PLAN_ALREADY_EXIST.format(
                        name = subscription_name
                    )
                )

            # Otherwise Create plan in razorpay

            razorpay_plan_data = self.payment_service.create_razorpay_plan(payload)

            # Now Extarct Plan_id and Item_id from razorpay_plan_data
            razorpay_plan_id = razorpay_plan_data["id"]
            razorpay_item_id = razorpay_plan_data["item"]["id"]
            razorpay_created_at = razorpay_plan_data["created_at"]
            razorpay_period = razorpay_plan_data["period"]
            razorpay_interval = razorpay_plan_data["interval"]

            # Now Add data to Subscription Plan DB
            plan_created = self.subscription_repo.create({
                "name": subscription_name,
                "description": payload.description,
                "price": payload.price,
                "razorpay_plan_id": razorpay_plan_id,
                "razorpay_item_id": razorpay_item_id,
                "period": razorpay_period,
                "interval": razorpay_interval,
                "currency": payload.currency,
                "created_at": razorpay_created_at,
                "duration": payload.duration
            })

            return success_response(
                status_code = http_status.HTTP_200_OK,
                msg = SuccessMessage.SUBSCRIPTION_PLAN_CREATED_SUCCESSFULLY,
                data = SubscriptionPlanResponse.model_validate(plan_created)
            )

        except HTTPException:
            raise
        except Exception as e:
            raise ServerException(e) from e

    # Get All Subscription Plans
    def get_all_subscription_plans(self, page: int = 1, page_size: int = 10):
        try:
            # Query base
            query = self.subscription_repo.db.query(self.subscription_repo.model).filter(
                self.subscription_repo.model.is_active.is_(True),
                self.subscription_repo.model.is_deleted.is_(False)
            )

            # Get total items count
            total_items = query.count()

            # Calculate total pages
            total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0

            # Calculate offset
            offset = (page - 1) * page_size

            # Fetch paginated plans
            plans = query.offset(offset).limit(page_size).all()

            # Validate and serialize
            validated_plans = [SubscriptionPlanResponse.model_validate(plan) for plan in plans]

            return pagination_response(
                data=validated_plans,
                message=SuccessMessage.SUBSCRIPTION_PLAN_FETCHED_SUCCESSFULLY,
                total_pages=total_pages,
                total_items=total_items,
                current_page=page,
                page_size=page_size
            )
        except Exception as e:
            raise ServerException(e) from e

    # Update Plan Details
    # def update_subscription_plan(self, )