from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class SpeciesBase(BaseModel):
    """Base schema for frog species."""
    common_name: str
    scientific_name: str
    description: Optional[str] = None
    habitat: Optional[str] = None
    range: Optional[str] = None
    image_url: Optional[str] = None
    audio_sample_url: Optional[str] = None


class SpeciesCreate(SpeciesBase):
    """Schema for creating a new species."""
    pass


class SpeciesUpdate(BaseModel):
    """Schema for updating a species."""
    common_name: Optional[str] = None
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    habitat: Optional[str] = None
    range: Optional[str] = None
    image_url: Optional[str] = None
    audio_sample_url: Optional[str] = None


class SpeciesResponse(SpeciesBase):
    """Schema for species response."""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SpeciesListResponse(BaseModel):
    """Schema for paginated species list."""
    items: List[SpeciesResponse]
    total: int
    skip: int
    limit: int
