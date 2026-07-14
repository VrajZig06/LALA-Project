from sqlalchemy.orm import Session

from app.db.models import Subscription
from app.repository.base_repository import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: Session):
        """
        Initialize Subscription repository.

        Args:
            db: Database session
        """
        super().__init__(Subscription, db)


    # Fetch Subscription that is related to user_id
    def fetch_current_subscription(self, user_id: str):
        current_subscription = self.db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.is_active == True,
            self.model.is_deleted == False,
        ).first()

        return current_subscription

    # Deactivate Current Subscription
    def cancelled_current_subscription(self, sub_id: str) -> int:
        updated_count = self.db.query(self.model).filter(
            self.model.id == sub_id
        ).update({
            self.model.status: "cancelled",
            self.model.is_active: False, 
            self.model.is_deleted: True
        })

        # Update to DB
        self.db.commit()

        return updated_count