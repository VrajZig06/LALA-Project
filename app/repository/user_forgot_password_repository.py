from sqlalchemy.orm import Session

from app.db.models.user_forgot_password_tracking import UserForgotPasswordTrack
from app.repository.base_repository import BaseRepository


class UserForgotPasswordRepository(BaseRepository[UserForgotPasswordTrack]):
    def __init__(self, db: Session):
        """
        Initialize UserForgotPasswordTrack repository.

        Args:
            db: Database session
        """
        super().__init__(UserForgotPasswordTrack, db)

    pass
