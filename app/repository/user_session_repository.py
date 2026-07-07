from sqlalchemy.orm import Session

from app.db.models.user_session import UserSession
from app.repository.base_repository import BaseRepository


class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self, db: Session):
        """
        Initialize UserSession repository.

        Args:
            db: Database session
        """
        super().__init__(UserSession, db)

    pass
