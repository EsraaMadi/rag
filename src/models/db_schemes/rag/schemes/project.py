from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship


# Defining the `Project` model, which represents the "projects" table in the database.
class Project(SQLAlchemyBase):

    # Specifying the name of the database table associated with this model.
    __tablename__ = "projects"
    
    # Primary key column for the table (integer ID that auto-increments).
    project_id = Column(Integer, primary_key=True, autoincrement=True)

    # UUID column for the project, which is unique (not sequential) and automatically generated.
    # It uses PostgreSQL's native UUID type and Python's `uuid.uuid4` to generate values.
    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Timestamp column for the creation time of the record.
    # `server_default=func.now()` ensures the value is set to the current time by the database.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Timestamp column for the last update time of the record.
    # `onupdate=func.now()` ensures the value is updated to the current time whenever the record is updated.
    # at creation time would be null
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Defining a one-to-many relationship with the `DataChunk` model.
    # `back_populates="project"` sets up a bidirectional relationship (defined in the `DataChunk` model).
    chunks = relationship("DataChunk", back_populates="project")

    # Defining a one-to-many relationship with the `Asset` model.
    # `back_populates="project"` sets up a bidirectional relationship (defined in the `Asset` model).
    assets = relationship("Asset", back_populates="project")
