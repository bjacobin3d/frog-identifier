from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.species import FrogSpecies


class Sighting(Base):
    """Model representing a frog sighting."""
    
    __tablename__ = "sightings"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    species_id: Mapped[int] = mapped_column(
        ForeignKey("frog_species.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    detection_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'audio' or 'image'
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    audio_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sighted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationships
    species: Mapped["FrogSpecies"] = relationship(
        "FrogSpecies", back_populates="sightings"
    )
    
    def __repr__(self) -> str:
        return f"<Sighting(id={self.id}, species_id={self.species_id}, type='{self.detection_type}')>"
