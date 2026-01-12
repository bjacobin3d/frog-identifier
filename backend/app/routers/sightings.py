import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.config import get_settings
from app.models.sighting import Sighting
from app.models.species import FrogSpecies
from app.schemas.sighting import (
    SightingResponse,
    SightingListResponse,
    SightingCreate,
    SightingUpdate,
    SightingStats,
)

router = APIRouter()
settings = get_settings()


async def save_upload_file(upload_file: UploadFile, subfolder: str) -> str:
    """Save an uploaded file and return the path."""
    ext = os.path.splitext(upload_file.filename)[1] if upload_file.filename else ""
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.upload_dir, subfolder, filename)
    
    content = await upload_file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    
    return f"/uploads/{subfolder}/{filename}"


@router.get("", response_model=SightingListResponse)
async def list_sightings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    species_id: Optional[int] = None,
    detection_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all sightings with optional filters."""
    query = select(Sighting)
    
    if species_id:
        query = query.where(Sighting.species_id == species_id)
    if detection_type:
        query = query.where(Sighting.detection_type == detection_type)
    if start_date:
        query = query.where(Sighting.sighted_at >= start_date)
    if end_date:
        query = query.where(Sighting.sighted_at <= end_date)
    
    query = query.order_by(desc(Sighting.sighted_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    sightings = result.scalars().all()
    
    # Get total count with same filters
    count_query = select(func.count(Sighting.id))
    if species_id:
        count_query = count_query.where(Sighting.species_id == species_id)
    if detection_type:
        count_query = count_query.where(Sighting.detection_type == detection_type)
    if start_date:
        count_query = count_query.where(Sighting.sighted_at >= start_date)
    if end_date:
        count_query = count_query.where(Sighting.sighted_at <= end_date)
    
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    return SightingListResponse(
        items=[SightingResponse.model_validate(s) for s in sightings],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/stats", response_model=SightingStats)
async def get_sighting_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get statistics about sightings."""
    # Total sightings
    total_result = await db.execute(select(func.count(Sighting.id)))
    total_sightings = total_result.scalar() or 0
    
    # Unique species
    species_result = await db.execute(
        select(func.count(func.distinct(Sighting.species_id)))
    )
    unique_species = species_result.scalar() or 0
    
    # By detection type
    audio_result = await db.execute(
        select(func.count(Sighting.id)).where(Sighting.detection_type == "audio")
    )
    audio_count = audio_result.scalar() or 0
    
    image_result = await db.execute(
        select(func.count(Sighting.id)).where(Sighting.detection_type == "image")
    )
    image_count = image_result.scalar() or 0
    
    # Recent sightings (last 30 days)
    thirty_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    recent_result = await db.execute(
        select(func.count(Sighting.id)).where(Sighting.sighted_at >= thirty_days_ago)
    )
    recent_count = recent_result.scalar() or 0
    
    # Top species
    top_species_query = (
        select(FrogSpecies.common_name, func.count(Sighting.id).label("count"))
        .join(Sighting, FrogSpecies.id == Sighting.species_id)
        .group_by(FrogSpecies.id)
        .order_by(desc("count"))
        .limit(5)
    )
    top_result = await db.execute(top_species_query)
    top_species = [{"name": row[0], "count": row[1]} for row in top_result.all()]
    
    return SightingStats(
        total_sightings=total_sightings,
        unique_species=unique_species,
        audio_identifications=audio_count,
        image_identifications=image_count,
        recent_sightings=recent_count,
        top_species=top_species,
    )


@router.get("/{sighting_id}", response_model=SightingResponse)
async def get_sighting(
    sighting_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific sighting by ID."""
    result = await db.execute(
        select(Sighting).where(Sighting.id == sighting_id)
    )
    sighting = result.scalar_one_or_none()
    
    if not sighting:
        raise HTTPException(status_code=404, detail="Sighting not found")
    
    return SightingResponse.model_validate(sighting)


@router.post("", response_model=SightingResponse, status_code=201)
async def create_sighting(
    species_id: int = Form(...),
    detection_type: str = Form(...),
    confidence_score: float = Form(...),
    notes: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    location_name: Optional[str] = Form(None),
    sighted_at: Optional[datetime] = Form(None),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """Create a new sighting."""
    # Verify species exists
    species_result = await db.execute(
        select(FrogSpecies).where(FrogSpecies.id == species_id)
    )
    if not species_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Species not found")
    
    # Handle file uploads
    image_path = None
    audio_path = None
    
    if image:
        image_path = await save_upload_file(image, "images")
    if audio:
        audio_path = await save_upload_file(audio, "audio")
    
    sighting = Sighting(
        species_id=species_id,
        detection_type=detection_type,
        confidence_score=confidence_score,
        notes=notes,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        image_path=image_path,
        audio_path=audio_path,
        sighted_at=sighted_at or datetime.utcnow(),
    )
    
    db.add(sighting)
    await db.commit()
    await db.refresh(sighting)
    
    return SightingResponse.model_validate(sighting)


@router.put("/{sighting_id}", response_model=SightingResponse)
async def update_sighting(
    sighting_id: int,
    sighting_data: SightingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a sighting (mainly for notes)."""
    result = await db.execute(
        select(Sighting).where(Sighting.id == sighting_id)
    )
    sighting = result.scalar_one_or_none()
    
    if not sighting:
        raise HTTPException(status_code=404, detail="Sighting not found")
    
    update_data = sighting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sighting, field, value)
    
    await db.commit()
    await db.refresh(sighting)
    
    return SightingResponse.model_validate(sighting)


@router.delete("/{sighting_id}", status_code=204)
async def delete_sighting(
    sighting_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a sighting."""
    result = await db.execute(
        select(Sighting).where(Sighting.id == sighting_id)
    )
    sighting = result.scalar_one_or_none()
    
    if not sighting:
        raise HTTPException(status_code=404, detail="Sighting not found")
    
    # Optionally delete associated files
    if sighting.image_path:
        filepath = os.path.join(".", sighting.image_path.lstrip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)
    if sighting.audio_path:
        filepath = os.path.join(".", sighting.audio_path.lstrip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)
    
    await db.delete(sighting)
    await db.commit()
