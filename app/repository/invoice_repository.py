from sqlalchemy.orm import Session

from app.db.models.invoices import Invoice
from app.repository.base_repository import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session):
        """
        Initialize Invoice repository.

        Args:
            db: Database session
        """
        super().__init__(Invoice, db)
