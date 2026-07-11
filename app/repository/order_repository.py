from sqlalchemy.orm import Session

from app.db.models.orders import Order
from app.repository.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        """
        Initialize Order repository.

        Args:
            db: Database session
        """
        super().__init__(Order, db)

    pass
