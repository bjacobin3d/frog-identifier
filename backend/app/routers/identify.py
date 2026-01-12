import io
import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.species import FrogSpecies
from app.schemas.identify import (
    IdentificationResult,
    PredictionItem,
    AudioIdentifyRequest,
)

router = APIRouter()


@router.post("/audio", response_model=IdentificationResult)
async def identify_audio(
    request: Request,
    audio: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Identify frog species from audio.
    
    Accepts either:
    - An audio file upload (WAV, WebM, MP3)
    - Base64-encoded audio in request body (for real-time streaming)
    """
    audio_classifier = request.app.state.audio_classifier
    
    if audio:
        # Handle file upload
        content = await audio.read()
        audio_bytes = io.BytesIO(content)
    else:
        # Handle base64 audio from request body
        try:
            body = await request.json()
            audio_data = body.get("audio_data")
            if not audio_data:
                raise HTTPException(
                    status_code=400, 
                    detail="No audio file or audio_data provided"
                )
            audio_bytes = io.BytesIO(base64.b64decode(audio_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid audio data: {str(e)}")
    
    # Run inference
    try:
        predictions = audio_classifier.predict(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio classification failed: {str(e)}")
    
    # Enrich predictions with species data from database
    enriched_predictions = []
    for pred in predictions[:5]:  # Top 5
        species_id = pred.get("species_id", 0)
        
        # Try to fetch from database if we have a valid ID
        species = None
        if species_id and species_id > 0:
            result = await db.execute(
                select(FrogSpecies).where(FrogSpecies.id == species_id)
            )
            species = result.scalar_one_or_none()
        
        enriched_predictions.append(PredictionItem(
            species_id=species_id if species_id else 0,
            common_name=species.common_name if species else pred.get("common_name", "Unknown Species"),
            scientific_name=species.scientific_name if species else pred.get("scientific_name", ""),
            confidence=pred["confidence"],
            image_url=species.image_url if species else None,
        ))
    
    # If no predictions, return empty result
    if not enriched_predictions:
        return IdentificationResult(
            detection_type="audio",
            predictions=[],
            top_prediction=None,
        )
    
    return IdentificationResult(
        detection_type="audio",
        predictions=enriched_predictions,
        top_prediction=enriched_predictions[0] if enriched_predictions else None,
    )


@router.post("/image", response_model=IdentificationResult)
async def identify_image(
    request: Request,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Identify frog species from an image.
    
    Accepts image files (JPEG, PNG, WebP).
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_classifier = request.app.state.image_classifier
    
    # Read image
    content = await image.read()
    image_bytes = io.BytesIO(content)
    
    # Run inference
    try:
        predictions = image_classifier.predict(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image classification failed: {str(e)}")
    
    # Enrich predictions with species data from database
    enriched_predictions = []
    for pred in predictions[:5]:  # Top 5
        species_id = pred.get("species_id", 0)
        
        # Try to fetch from database if we have a valid ID
        species = None
        if species_id and species_id > 0:
            result = await db.execute(
                select(FrogSpecies).where(FrogSpecies.id == species_id)
            )
            species = result.scalar_one_or_none()
        
        enriched_predictions.append(PredictionItem(
            species_id=species_id if species_id else 0,
            common_name=species.common_name if species else pred.get("common_name", "Unknown Species"),
            scientific_name=species.scientific_name if species else pred.get("scientific_name", ""),
            confidence=pred["confidence"],
            image_url=species.image_url if species else None,
        ))
    
    # If no predictions, return empty result
    if not enriched_predictions:
        return IdentificationResult(
            detection_type="image",
            predictions=[],
            top_prediction=None,
        )
    
    return IdentificationResult(
        detection_type="image",
        predictions=enriched_predictions,
        top_prediction=enriched_predictions[0] if enriched_predictions else None,
    )


@router.post("/audio/stream", response_model=IdentificationResult)
async def identify_audio_stream(
    request: Request,
    audio_request: AudioIdentifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Identify frog species from streamed audio chunks.
    
    Accepts base64-encoded audio data for real-time identification.
    """
    audio_classifier = request.app.state.audio_classifier
    
    try:
        audio_bytes = io.BytesIO(base64.b64decode(audio_request.audio_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
    
    # Run inference
    try:
        predictions = audio_classifier.predict(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio classification failed: {str(e)}")
    
    # Enrich predictions with species data
    enriched_predictions = []
    for pred in predictions[:5]:
        result = await db.execute(
            select(FrogSpecies).where(FrogSpecies.id == pred["species_id"])
        )
        species = result.scalar_one_or_none()
        
        enriched_predictions.append(PredictionItem(
            species_id=pred["species_id"],
            common_name=species.common_name if species else pred.get("common_name", "Unknown"),
            scientific_name=species.scientific_name if species else pred.get("scientific_name", ""),
            confidence=pred["confidence"],
            image_url=species.image_url if species else None,
        ))
    
    return IdentificationResult(
        detection_type="audio",
        predictions=enriched_predictions,
        top_prediction=enriched_predictions[0] if enriched_predictions else None,
    )
