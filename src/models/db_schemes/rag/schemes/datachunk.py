from pydantic import BaseModel
from .rag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid


class DataChunk(SQLAlchemyBase):
    """
    Represents a chunk of data stored in the database.
    """
    # Specifying the name of the database table associated with this model.
    __tablename__ = "chunks"
    
    # Primary identifier fields
    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    # Content fields
    chunk_text = Column(String, nullable=False)  # The actual text content of the chunk
    chunk_metadata = Column(JSONB, nullable=True)  # Additional metadata stored as JSON
    chunk_order = Column(Integer, nullable=False)  # Ordering of chunks
    
    # Foreign key relationships
    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)  # Many chunks belong to one project
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)  # Many chunks belong to one asset
    
    # Timestamp fields for auditing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationship definitions (many-to-one relationships)
    project = relationship("Project", back_populates="chunks")  # Many chunks to one project
    asset = relationship("Asset", back_populates="chunks")  # Many chunks to one asset
    
    # Database optimizations: indexes for frequently queried columns
    __table_args__ = (
        Index('ix_chunk_project_id', chunk_project_id),  # Index to speed up queries filtering by project
        Index('ix_chunk_asset_id', chunk_asset_id),  # Index to speed up queries filtering by asset
    )

class RetrievedDocument(BaseModel):
    """
    Pydantic model representing a retrieved document with its relevance score.
    Used for API responses when returning search results.
    """
    text: str  # The content of the retrieved document
    score: float  # Relevance score of the document to the query
