"""
Base repository class with common CRUD operations.
"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations."""

    def __init__(self, model: type[ModelType], db: Session):
        """
        Initialize repository.

        Args:
            model: The SQLAlchemy model class
            db: Database session
        """
        super().__init__()
        self.model = model
        self.db = db

    def get(self, id: str) -> ModelType | None:
        """
        Get a record by ID.

        Args:
            id: The record ID

        Returns:
            The model instance or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_field(self, field_name: str, value: Any) -> ModelType | None:
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
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> list[ModelType]:
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
                    query = query.filter(
                        getattr(self.model, field) == value,
                        self.model.is_active == True,
                        self.model.is_deleted == False,
                    )

        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: dict[str, Any] | BaseModel) -> ModelType:
        if isinstance(obj_in, BaseModel):
            data = obj_in.model_dump()
        else:
            data = obj_in

        db_obj = self.model(**data)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
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
    
    def create_all(self, list_obj_in: list[dict[str, Any]] | list[BaseModel]) -> ModelType:
        db_data = []
        for obj_in in list_obj_in:
            if isinstance(obj_in, BaseModel):
                data = obj_in.model_dump()
            else:
                data = obj_in

            db_obj = self.model(**data)
            db_data.append(db_obj)

        # Now add All to DB
        self.db.add_all(db_data)
        self.db.commit()

        return True

