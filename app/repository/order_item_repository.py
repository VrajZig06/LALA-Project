from sqlalchemy.orm import Session

from app.db.models.order_items import OrderItem
from app.repository.base_repository import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    def __init__(self, db: Session):
        """
        Initialize OrderItem repository.

        Args:
            db: Database session
        """
        super().__init__(OrderItem, db)

    pass
