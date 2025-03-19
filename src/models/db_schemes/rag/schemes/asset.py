from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid


# Defining the `Asset` model, which represents the "assets" table in the database.
class Asset(SQLAlchemyBase):

    # Specifying the name of the database table associated with this model.
    __tablename__ = "assets"

    # Primary key column for the table (integer ID that auto-increments).
    asset_id = Column(Integer, primary_key=True, autoincrement=True)

    # UUID column for the asset, which is unique and automatically generated using `uuid.uuid4`.
    asset_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    # Column for the type of the asset (e.g., image, video, etc.), stored as a string.
    asset_type = Column(String, nullable=False)

    # Column for the name of the asset, stored as a string.
    asset_name = Column(String, nullable=False)

    # Column for the size of the asset (e.g., in bytes), stored as an integer.
    asset_size = Column(Integer, nullable=False)

    # Column for the configuration or metadata of the asset, stored as JSONB (specific to PostgreSQL).
    asset_config = Column(JSONB, nullable=True)

    # Foreign key column linking this asset to a specific project in the "projects" table.
    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    # Timestamp column for the creation time of the record.
    # `server_default=func.now()` ensures the value is set to the current time by the database.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Timestamp column for the last update time of the record.
    # `onupdate=func.now()` ensures the value is updated to the current time whenever the record is updated.
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Defining a many-to-one relationship with the `Project` model.
    # `back_populates="assets"` sets up a bidirectional relationship (defined in the `Project` model).
    project = relationship("Project", back_populates="assets")

    # Defining a one-to-many relationship with the `DataChunk` model.
    # `back_populates="asset"` sets up a bidirectional relationship (defined in the `DataChunk` model).
    chunks = relationship("DataChunk", back_populates="asset")

    # Adding table-level arguments, such as indexes, for optimizing queries.
    __table_args__ = (
        # Index on `asset_project_id` to improve lookup performance when filtering by project.
        Index('ix_asset_project_id', asset_project_id),
        # Index on `asset_type` to optimize queries involving asset type filtering.
        Index('ix_asset_type', asset_type),
    )