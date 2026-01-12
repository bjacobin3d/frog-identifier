import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routers import species, sightings, identify, realtime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("Starting Frog Identifier API")
    
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.upload_dir, "audio"), exist_ok=True)
    
    await init_db()
    logger.info("Database initialized")
    
    # Load audio classifier (BirdNET preferred, fallback to basic)
    try:
        from app.ml.birdnet_classifier import BirdNetAudioClassifier, BIRDNET_AVAILABLE
        if BIRDNET_AVAILABLE:
            app.state.audio_classifier = BirdNetAudioClassifier()
            if app.state.audio_classifier.available:
                logger.info("BirdNET audio classifier loaded")
            else:
                raise ImportError("BirdNET failed to initialize")
        else:
            raise ImportError("BirdNET not installed")
    except Exception as e:
        logger.warning("BirdNET not available (%s), using fallback classifier", e)
        from app.ml.audio_classifier import AudioClassifier
        app.state.audio_classifier = AudioClassifier()
    
    # Load image classifier (HuggingFace CLIP preferred, fallback to basic)
    try:
        from app.ml.huggingface_classifier import HuggingFaceImageClassifier, TRANSFORMERS_AVAILABLE
        if TRANSFORMERS_AVAILABLE:
            app.state.image_classifier = HuggingFaceImageClassifier()
            if app.state.image_classifier.available:
                logger.info("HuggingFace CLIP image classifier loaded")
            else:
                raise ImportError("HuggingFace failed to initialize")
        else:
            raise ImportError("transformers not installed")
    except Exception as e:
        logger.warning("HuggingFace not available (%s), using fallback classifier", e)
        from app.ml.image_classifier import ImageClassifier
        app.state.image_classifier = ImageClassifier()
    
    logger.info("ML models loaded")
    logger.info("Frog Identifier API ready")
    
    yield
    
    logger.info("Shutting down Frog Identifier API")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Identify frogs by their calls and photos. Build your personal frog library.",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(species.router, prefix="/api/v1/species", tags=["Species"])
app.include_router(sightings.router, prefix="/api/v1/sightings", tags=["Sightings"])
app.include_router(identify.router, prefix="/api/v1/identify", tags=["Identification"])
app.include_router(realtime.router, prefix="/api/v1/realtime", tags=["Real-time"])


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for API health check."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "models": {
            "audio": "loaded",
            "image": "loaded",
        },
    }
