from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.species import FrogSpecies
from app.schemas.species import (
    SpeciesResponse,
    SpeciesListResponse,
    SpeciesCreate,
    SpeciesUpdate,
)

router = APIRouter()


@router.get("", response_model=SpeciesListResponse)
async def list_species(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all frog species with optional search."""
    query = select(FrogSpecies)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (FrogSpecies.common_name.ilike(search_term)) |
            (FrogSpecies.scientific_name.ilike(search_term))
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    species = result.scalars().all()
    
    # Get total count
    count_query = select(FrogSpecies)
    if search:
        count_query = count_query.where(
            (FrogSpecies.common_name.ilike(search_term)) |
            (FrogSpecies.scientific_name.ilike(search_term))
        )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return SpeciesListResponse(
        items=[SpeciesResponse.model_validate(s) for s in species],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{species_id}", response_model=SpeciesResponse)
async def get_species(
    species_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific frog species by ID."""
    result = await db.execute(
        select(FrogSpecies).where(FrogSpecies.id == species_id)
    )
    species = result.scalar_one_or_none()
    
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    return SpeciesResponse.model_validate(species)


@router.post("", response_model=SpeciesResponse, status_code=201)
async def create_species(
    species_data: SpeciesCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new frog species."""
    species = FrogSpecies(**species_data.model_dump())
    db.add(species)
    await db.commit()
    await db.refresh(species)
    return SpeciesResponse.model_validate(species)


@router.put("/{species_id}", response_model=SpeciesResponse)
async def update_species(
    species_id: int,
    species_data: SpeciesUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a frog species."""
    result = await db.execute(
        select(FrogSpecies).where(FrogSpecies.id == species_id)
    )
    species = result.scalar_one_or_none()
    
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    update_data = species_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(species, field, value)
    
    await db.commit()
    await db.refresh(species)
    return SpeciesResponse.model_validate(species)


@router.delete("/{species_id}", status_code=204)
async def delete_species(
    species_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a frog species."""
    result = await db.execute(
        select(FrogSpecies).where(FrogSpecies.id == species_id)
    )
    species = result.scalar_one_or_none()
    
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    await db.delete(species)
    await db.commit()


@router.get("/{species_id}/calls")
async def get_species_calls(
    species_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get audio sample URLs for a specific species."""
    result = await db.execute(
        select(FrogSpecies).where(FrogSpecies.id == species_id)
    )
    species = result.scalar_one_or_none()
    
    if not species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    return {
        "species_id": species.id,
        "common_name": species.common_name,
        "audio_samples": [species.audio_sample_url] if species.audio_sample_url else [],
    }
