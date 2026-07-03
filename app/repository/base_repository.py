"""
Base repository class with common CRUD operations.
"""

from typing import Generic, TypeVar, Optional, Type, List, Any, Dict, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository.

        Args:
            model: The SQLAlchemy model class
            db: Database session
        """
        super().__init__()
        self.model = model
        self.db = db

    def get(self, id: str) -> Optional[ModelType]:
        """
        Get a record by ID.

        Args:
            id: The record ID

        Returns:
            The model instance or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id, self.model.is_active == True, self.model.is_deleted == False).first()

    def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """
        Get a record by a specific field.

        Args:
            field_name: The field name to filter by
            value: The value to match

        Returns:
            The model instance or None if not found
        """
        return (
            self.db.query(self.model)
            .filter(getattr(self.model, field_name) == value)
            .first()
        )

    def get_all(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all records with optional filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional dictionary of field-value pairs to filter by

        Returns:
            List of model instances
        """
        query = self.db.query(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: Union[Dict[str, Any], BaseModel]) -> ModelType:
        if isinstance(obj_in, BaseModel):
            data = obj_in.model_dump()
        else:
            data = obj_in

        db_obj = self.model(**data)

        self.db.add(db_obj)
        self.db.commit()
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.flush()
        self.db.commit()

        return db_obj

    def delete(self, id: str) -> bool:
        obj = self.get(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.flush()
        return True
