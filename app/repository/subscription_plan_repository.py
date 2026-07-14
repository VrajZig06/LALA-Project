from sqlalchemy.orm import Session

from app.db.models.subscription_plan import SubscriptionPlan
from app.repository.base_repository import BaseRepository


class SubscriptionPlanRepository(BaseRepository[SubscriptionPlan]):
    def __init__(self, db: Session):
        """
        Initialize SubscriptionPlan repository.

        Args:
            db: Database session
        """
        super().__init__(SubscriptionPlan, db)

    pass
