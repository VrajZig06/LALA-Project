from sqlalchemy.orm import Session

from app.db.models.payment_transactions import PaymentTransaction
from app.repository.base_repository import BaseRepository


class PaymentTransactionRepository(BaseRepository[PaymentTransaction]):
    def __init__(self, db: Session):
        """
        Initialize PaymentTransaction repository.

        Args:
            db: Database session
        """
        super().__init__(PaymentTransaction, db)

    pass
