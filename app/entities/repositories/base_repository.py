from typing import Any, Dict, Generic, List, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.clients.db.postgres_client import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ModelSchemaType = TypeVar("ModelSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class providing common database operations.

    This class implements basic CRUD operations that can be inherited by specific repositories.
    It uses SQLAlchemy for database operations and Pydantic for data validation.

    Type Parameters:
        ModelType: The SQLAlchemy model type
        CreateSchemaType: The Pydantic schema type for creation
        UpdateSchemaType: The Pydantic schema type for updates

    Attributes:
        model: The SQLAlchemy model class
        model_schema: The Pydantic schema class for the model
    """

    def __init__(self, model: Type[ModelType], model_schema: Type[ModelSchemaType]):
        """Initialize the repository with model and schema classes.

        Args:
            model: The SQLAlchemy model class
            model_schema: The Pydantic schema class for the model
        """
        self.model = model
        self.model_schema = model_schema

    def get_all(self, db: Session) -> List[ModelSchemaType]:
        """Get all records from the database.

        Args:
            db: Database session

        Returns:
            List of model schemas
        """
        return [
            self.model_schema.model_validate(obj)
            for obj in db.query(self.model).order_by(self.model.id.desc()).all()
        ]

    def get_paginated(
        self, db: Session, *, offset: int = 0, limit: int = 10
    ) -> List[ModelSchemaType]:
        """Get paginated records from the database.

        Args:
            db: Database session
            offset: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model schemas
        """
        return [
            self.model_schema.model_validate(obj)
            for obj in db.query(self.model)
            .order_by(self.model.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        ]

    def get_by_id(self, db: Session, id: int) -> ModelSchemaType:
        """Get a record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model schema if found, None otherwise
        """
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if not db_obj:
            return None
        return self.model_schema.model_validate(db_obj)

    def get_multiple_by_ids(self, db: Session, ids: List[int]) -> List[ModelSchemaType]:
        return [
            self.model_schema.model_validate(obj)
            for obj in db.query(self.model).filter(self.model.id.in_(ids)).all()
        ]

    def get_by_field(self, db: Session, **kwargs) -> ModelSchemaType:
        """Get a record by field values.

        Args:
            db: Database session
            **kwargs: Field names and values to filter by

        Returns:
            Model schema if found, None otherwise
        """
        query = db.query(self.model)
        for field, value in kwargs.items():
            query = query.filter(getattr(self.model, field) == value)
        db_obj = query.first()
        if db_obj:
            return self.model_schema.model_validate(db_obj)
        return None

    def get_by_field_list(
        self, db: Session, order_by: str = None, desc: bool = False, **kwargs
    ) -> List[ModelSchemaType]:
        """Get all records matching field values.

        Args:
            db: Database session
            order_by: Optional field name to order results by
            desc: Whether to order in descending order (default: False)
            **kwargs: Field names and values to filter by

        Returns:
            List of model schemas
        """
        query = db.query(self.model)
        for field, value in kwargs.items():
            query = query.filter(getattr(self.model, field) == value)
        if order_by:
            order_field = getattr(self.model, order_by)
            query = query.order_by(order_field.desc() if desc else order_field)
        return [self.model_schema.model_validate(obj) for obj in query.all()]

    def count(self, db: Session, **kwargs) -> int:
        """Get the total count of records in the database.

        Args:
            db: Database session

        Returns:
            Total number of records
        """
        return db.query(self.model).count()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelSchemaType:
        """Create a new record.

        Args:
            db: Database session
            obj_in: Creation schema with new record data

        Returns:
            Created model schema
        """
        obj_in_data = jsonable_encoder(obj_in)
        relevant_keys = {
            k: v for k, v in obj_in_data.items() if k in self.model.__table__.columns
        }
        db_obj = self.model(**relevant_keys)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return self.model_schema.model_validate(db_obj)

    def create_bulk(
        self, db: Session, obj_list: List[CreateSchemaType]
    ) -> List[ModelSchemaType]:
        """Create multiple records in bulk.

        Args:
            db: Database session
            obj_list: List of creation schemas with new record data

        Returns:
            List of created model schemas
        """
        db_objs = []
        for obj_in in obj_list:
            obj_in_data = jsonable_encoder(obj_in)
            relevant_keys = {
                k: v
                for k, v in obj_in_data.items()
                if k in self.model.__table__.columns
            }
            db_obj = self.model(**relevant_keys)
            db_objs.append(db_obj)

        db.add_all(db_objs)
        db.commit()

        # Refresh all objects to get their IDs
        for db_obj in db_objs:
            db.refresh(db_obj)

        return [self.model_schema.model_validate(obj) for obj in db_objs]

    def _update_obj(
        self,
        db: Session,
        db_obj: ModelType,
        update_schema: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Helper method to update a database object with new values.

        Args:
            db: Database session
            db_obj: Database object to update
            update_schema: Update schema or dict with new values

        Returns:
            Updated model
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(update_schema, dict):
            update_data = update_schema
        else:
            update_data = update_schema.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return self.model_schema.model_validate(db_obj)

    def update_by_id(
        self,
        db: Session,
        *,
        id: int,
        update_schema: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an existing record.

        Args:
            db: Database session
            id: ID of the record to update
            update_schema: Update schema or dict with new values

        Returns:
            Updated model or None if not found
        """
        db_obj = db.query(self.model).filter(self.model.id == id).first()
        if not db_obj:
            return None
        return self._update_obj(db, db_obj, update_schema)

    def update_by_field(
        self,
        db: Session,
        *,
        fields: Dict[str, Any],
        update_schema: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update a record by field values.

        Args:
            db: Database session
            fields: Dictionary of field names and values to filter by
            update_schema: Update schema or dict with new values

        Returns:
            Updated model or None if not found
        """
        query = db.query(self.model)
        for field, value in fields.items():
            query = query.filter(getattr(self.model, field) == value)

        db_obj = query.first()
        if not db_obj:
            return None
        return self._update_obj(db, db_obj, update_schema)

    def update_multiple_by_ids(
        self,
        db: Session,
        *,
        ids: List[int],
        update_schema: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> int:
        """Update multiple records by their IDs using a single SQL UPDATE statement.

        Args:
            db: Database session
            ids: List of record IDs to update
            update_schema: Update schema or dict with new values

        Returns:
            Number of records updated
        """
        if not ids:
            return 0

        # Prepare update data
        if isinstance(update_schema, dict):
            update_data = update_schema
        else:
            update_data = update_schema.model_dump(exclude_unset=True)

        if not update_data:
            return 0

        # Generate a single UPDATE statement with IN clause
        # This is much more efficient than individual updates
        result = (
            db.query(self.model)
            .filter(self.model.id.in_(ids))
            .update(update_data, synchronize_session=False)
        )

        # Commit the changes
        db.commit()

        return result

    def remove_by_id(self, db: Session, *, id: int) -> ModelSchemaType:
        """Delete a record by ID.

        Args:
            db: Database session
            id: ID of record to delete

        Returns:
            Deleted model schema
        """
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            return None

        # Store the schema before deletion
        result_schema = self.model_schema.model_validate(obj)

        # Delete and flush to trigger cascades
        db.delete(obj)
        db.flush()  # This triggers the CASCADE operations
        db.commit()

        return result_schema

    def remove_by_field(self, db: Session, **kwargs) -> List[ModelSchemaType]:
        """Delete records by field values.

        Args:
            db: Database session
            **kwargs: Field names and values to filter by

        Returns:
            List of deleted model schemas
        """
        query = db.query(self.model)
        for field, value in kwargs.items():
            query = query.filter(getattr(self.model, field) == value)
        objs = query.all()
        deleted_schemas = [self.model_schema.model_validate(obj) for obj in objs]
        for obj in objs:
            db.delete(obj)
        if objs:
            db.commit()
        return deleted_schemas

    def search(self, db: Session, search_query: str, **kwargs) -> List[ModelSchemaType]:
        """Search records with LIKE operator on search_query and optional exact matches.

        Args:
            db: Database session
            search_query: Value to use with LIKE operator
            **kwargs: Additional field=value pairs for exact matching

        Returns:
            List of matching model schemas
        """
        query = db.query(self.model)

        # Add exact match filters from kwargs
        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        # Add LIKE filter on name field
        if hasattr(self.model, "name"):
            query = query.filter(self.model.name.ilike(f"%{search_query}%"))
        else:
            return []

        results = query.all()
        return [self.model_schema.model_validate(item) for item in results]
