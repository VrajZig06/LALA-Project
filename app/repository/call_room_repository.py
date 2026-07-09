from sqlalchemy.orm import Session

from app.db.models.call_room import CallRoom
from app.repository.base_repository import BaseRepository


class CallRoomRepository(BaseRepository[CallRoom]):
    def __init__(self, db: Session):
        """
        Initialize call room repository.

        Args:
            db: Database session
        """
        super().__init__(CallRoom, db)

    def get_by_code(self, room_code: str) -> CallRoom | None:
        """
        Retrieve an active call room by its room code.
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.room_code == room_code,
                self.model.is_active == True,
                self.model.is_deleted == False,
            )
            .first()
        )
