from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict


class SightingBase(BaseModel):
    """Base schema for sightings."""
    species_id: int
    detection_type: str
    confidence_score: float
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None


class SightingCreate(SightingBase):
    """Schema for creating a new sighting."""
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    sighted_at: Optional[datetime] = None


class SightingUpdate(BaseModel):
    """Schema for updating a sighting."""
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None


class SightingResponse(SightingBase):
    """Schema for sighting response."""
    id: int
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    sighted_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SightingListResponse(BaseModel):
    """Schema for paginated sighting list."""
    items: List[SightingResponse]
    total: int
    skip: int
    limit: int


class SpeciesCount(BaseModel):
    """Schema for species count in stats."""
    name: str
    count: int


class SightingStats(BaseModel):
    """Schema for sighting statistics."""
    total_sightings: int
    unique_species: int
    audio_identifications: int
    image_identifications: int
    recent_sightings: int
    top_species: List[Any]
