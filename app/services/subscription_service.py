
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
from app.schema.subscription import SubscriptionPlanCreate, SubscriptionPlanResponse, SubscriptionCreate, SubscriptionCreateResponse, CancelSubscription
from app.services.payment_service import PaymentService
from app.repository.subscription_repository import SubscriptionRepository
from app.common.utils import get_unix_time

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
        self.subscription_plan_repo = SubscriptionPlanRepository(db)
        self.subscription_repo = SubscriptionRepository(db)

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
            query = self.subscription_repo.db.query(self.subscription_plan_repo.model).filter(
                self.subscription_plan_repo.model.is_active.is_(True),
                self.subscription_plan_repo.model.is_deleted.is_(False)
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

    # Create Subscription
    def create_subbscription(self, payload: SubscriptionCreate, current_user: dict):
        try:
            # Extract User Id and Plan Id
            plan_id = payload.plan_id
            current_user_id = current_user.get("id")
        

            # Check Plan exist in DB
            plan_detail = self.subscription_plan_repo.get(plan_id)

            if not plan_detail or not plan_detail.is_active:
                raise HTTPException(
                    status_code = http_status.HTTP_404_NOT_FOUND,
                    detail = ErrorMessage.SUBSCRIPTION_PLAN_NOT_FOUND
                )

            # Check first Subscription is Active for current user
            is_subscription_exist = self.subscription_repo.get_by_field("user_id", current_user_id) 

            # Raise Subscription already exists
            if is_subscription_exist and is_subscription_exist.is_active and not is_subscription_exist.is_deleted:
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.SUBSCRIPTION_ALREADY_EXIST
                )

            # Create New User Subscription payload
            razorpay_subscription_payload = {
                "plan_id": plan_detail.razorpay_plan_id,
                "total_count": plan_detail.duration,
                "quantity": 1,
                "customer_notify": True,
                "notes": {
                    "user_id" : current_user_id
                }
            }

            # Create Subscription in Razorpay 
            razorpay_subscription_response = self.payment_service.create_subscription(razorpay_subscription_payload)

            # Now Store Subscription details to DB 
            new_subscription_detail = {
                "user_id" : razorpay_subscription_response.get("notes", {}).get("user_id"),
                "plan_id": plan_id,
                "razorpay_subscription_id": razorpay_subscription_response.get("id"),
                "status": razorpay_subscription_response.get("status", "created"),
                "quantity": razorpay_subscription_response.get("quantity", 1),
                "cancel_at_cycle_end": razorpay_subscription_response.get("has_scheduled_changes", False),
                "current_period_start": razorpay_subscription_response.get("current_start"),
                "current_period_end": razorpay_subscription_response.get("current_end"),
                "ended_at": razorpay_subscription_response.get("end_at")
            }

            db_subscription_data = self.subscription_repo.create(new_subscription_detail)

            return success_response(
                status_code= http_status.HTTP_200_OK,
                msg= SuccessMessage.SUBSCRIPTION_CREATED_SUCCESSFULLY,
                data= SubscriptionCreateResponse.model_validate(db_subscription_data)
            )

        except HTTPException:
            raise 
        except Exception as e:
            raise ServerException(e)

    # Cancel User Subscription
    def cancel_subscription(self, payload: CancelSubscription, current_user: dict):
        try:
            sub_id = payload.subscription_id
            user_id = current_user.get("id")

            # Check for user subscription is active 
            current_subscription = self.subscription_repo.fetch_current_subscription(user_id)

            if not current_subscription or current_subscription.id != sub_id:
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.SUBSCRIPTION_NOT_EXIST
                )
            
            # Extract Razorpay Subscription ID
            razorpay_subscription_id = current_subscription.razorpay_subscription_id

            # Cancel it From Razorpay Platform 
            razorpay_cancel_sub_res = self.payment_service.cancel_subscription({
                "subscription_id": razorpay_subscription_id,
                "at_cycle_end": payload.at_cycle_end
            })  

            # Update DB for immidiate cancel subscription
            if not payload.at_cycle_end:
                # Update DB for Immidate
                self.subscription_repo.cancelled_current_subscription(current_subscription.id)


            return success_response(
                status_code= http_status.HTTP_200_OK,
                msg= SuccessMessage.SUBSCRIPTION_CANCELLED_SUCCESSFULLY,
                data = {
                    "id": current_subscription.id,
                    "status": razorpay_cancel_sub_res.get("status")
                }
            )
        except HTTPException:
            raise 
        except Exception as e:
            raise ServerException(e) 

    # Updgrade or Downgrade subscription
    def update_subscription(self):
        try:
            pass
        except HTTPException:
            raise 
        except Exception as e:
            raise ServerException(e) 