from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.sighting import Sighting


class FrogSpecies(Base):
    """Model representing a frog species."""
    
    __tablename__ = "frog_species"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    common_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scientific_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    habitat: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    range: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_sample_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationships
    sightings: Mapped[List["Sighting"]] = relationship(
        "Sighting", back_populates="species", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<FrogSpecies(id={self.id}, name='{self.common_name}')>"
