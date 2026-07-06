from sqlalchemy.orm import Session

from app.db.models.user import User
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        """
        Initialize user repository.

        Args:
            db: Database session
        """
        super().__init__(User, db)

    pass
