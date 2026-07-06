from sqlalchemy.orm import Session

from app.db.models.role import Role
from app.repository.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        """
        Initialize user repository.

        Args:
            db: Database session
        """
        super().__init__(Role, db)

    pass
