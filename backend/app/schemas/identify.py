from typing import Optional, List

from pydantic import BaseModel


class PredictionItem(BaseModel):
    """Schema for a single prediction result."""
    species_id: int
    common_name: str
    scientific_name: str
    confidence: float
    image_url: Optional[str] = None


class IdentificationResult(BaseModel):
    """Schema for identification results."""
    detection_type: str  # 'audio' or 'image'
    predictions: List[PredictionItem]
    top_prediction: Optional[PredictionItem] = None


class AudioIdentifyRequest(BaseModel):
    """Schema for audio identification via base64."""
    audio_data: str  # Base64-encoded audio
    sample_rate: Optional[int] = 44100
    format: Optional[str] = "webm"  # webm, wav, mp3
