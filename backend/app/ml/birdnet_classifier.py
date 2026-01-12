"""
BirdNET-based audio classifier for frog call identification.

Uses Cornell Lab of Ornithology's BirdNET model which supports
identification of birds, frogs, and other wildlife sounds.
"""

import io
import logging
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from birdnetlib import Recording
    from birdnetlib.analyzer import Analyzer
    BIRDNET_AVAILABLE = True
except ImportError:
    BIRDNET_AVAILABLE = False
    logger.warning("BirdNET not installed. Run: pip install birdnetlib tensorflow")


# Mapping of BirdNET species names to our database IDs
# BirdNET uses scientific names, we map to our species
SPECIES_MAPPING = {
    # Frogs - BirdNET format is typically "Common Name_Scientific Name"
    "Spring Peeper_Pseudacris crucifer": {"id": 2, "common_name": "Spring Peeper", "scientific_name": "Pseudacris crucifer"},
    "American Bullfrog_Lithobates catesbeianus": {"id": 1, "common_name": "American Bullfrog", "scientific_name": "Lithobates catesbeianus"},
    "Green Treefrog_Hyla cinerea": {"id": 3, "common_name": "Green Tree Frog", "scientific_name": "Hyla cinerea"},
    "Pacific Treefrog_Pseudacris regilla": {"id": 4, "common_name": "Pacific Tree Frog", "scientific_name": "Pseudacris regilla"},
    "Wood Frog_Lithobates sylvaticus": {"id": 5, "common_name": "Wood Frog", "scientific_name": "Lithobates sylvaticus"},
    "Gray Treefrog_Hyla versicolor": {"id": 6, "common_name": "Gray Tree Frog", "scientific_name": "Hyla versicolor"},
    "Northern Leopard Frog_Lithobates pipiens": {"id": 7, "common_name": "Northern Leopard Frog", "scientific_name": "Lithobates pipiens"},
    "Green Frog_Lithobates clamitans": {"id": 8, "common_name": "Green Frog", "scientific_name": "Lithobates clamitans"},
    "Pickerel Frog_Lithobates palustris": {"id": 9, "common_name": "Pickerel Frog", "scientific_name": "Lithobates palustris"},
    "Western Chorus Frog_Pseudacris triseriata": {"id": 10, "common_name": "Western Chorus Frog", "scientific_name": "Pseudacris triseriata"},
    "Northern Cricket Frog_Acris crepitans": {"id": 11, "common_name": "Northern Cricket Frog", "scientific_name": "Acris crepitans"},
    "Cope's Gray Treefrog_Hyla chrysoscelis": {"id": 12, "common_name": "Cope's Gray Treefrog", "scientific_name": "Hyla chrysoscelis"},
    "Barking Treefrog_Hyla gratiosa": {"id": 13, "common_name": "Barking Treefrog", "scientific_name": "Hyla gratiosa"},
    "Squirrel Treefrog_Hyla squirella": {"id": 14, "common_name": "Squirrel Treefrog", "scientific_name": "Hyla squirella"},
    "Southern Leopard Frog_Lithobates sphenocephalus": {"id": 15, "common_name": "Southern Leopard Frog", "scientific_name": "Lithobates sphenocephalus"},
    "Pig Frog_Lithobates grylio": {"id": 16, "common_name": "Pig Frog", "scientific_name": "Lithobates grylio"},
    "River Frog_Lithobates heckscheri": {"id": 17, "common_name": "River Frog", "scientific_name": "Lithobates heckscheri"},
    "Crawfish Frog_Lithobates areolatus": {"id": 18, "common_name": "Crawfish Frog", "scientific_name": "Lithobates areolatus"},
    "Gopher Frog_Lithobates capito": {"id": 19, "common_name": "Gopher Frog", "scientific_name": "Lithobates capito"},
    "Carpenter Frog_Lithobates virgatipes": {"id": 20, "common_name": "Carpenter Frog", "scientific_name": "Lithobates virgatipes"},
    
    # Tennessee species
    "American Toad_Anaxyrus americanus": {"id": 21, "common_name": "American Toad", "scientific_name": "Anaxyrus americanus"},
    "Fowler's Toad_Anaxyrus fowleri": {"id": 22, "common_name": "Fowler's Toad", "scientific_name": "Anaxyrus fowleri"},
    "Southern Cricket Frog_Acris gryllus": {"id": 23, "common_name": "Southern Cricket Frog", "scientific_name": "Acris gryllus"},
    "Bird-voiced Treefrog_Dryophytes avivoca": {"id": 24, "common_name": "Bird-voiced Treefrog", "scientific_name": "Dryophytes avivoca"},
    "Mountain Chorus Frog_Pseudacris brachyphona": {"id": 25, "common_name": "Mountain Chorus Frog", "scientific_name": "Pseudacris brachyphona"},
    "Upland Chorus Frog_Pseudacris feriarum": {"id": 26, "common_name": "Upland Chorus Frog", "scientific_name": "Pseudacris feriarum"},
    "Eastern Narrow-mouthed Toad_Gastrophryne carolinensis": {"id": 27, "common_name": "Eastern Narrow-mouthed Toad", "scientific_name": "Gastrophryne carolinensis"},
    
    # Alternative name formats BirdNET might use
    "Pseudacris crucifer_Spring Peeper": {"id": 2, "common_name": "Spring Peeper", "scientific_name": "Pseudacris crucifer"},
    "Lithobates catesbeianus_American Bullfrog": {"id": 1, "common_name": "American Bullfrog", "scientific_name": "Lithobates catesbeianus"},
}

# Also create a lookup by scientific name only
SCIENTIFIC_NAME_MAPPING = {
    "Pseudacris crucifer": {"id": 2, "common_name": "Spring Peeper", "scientific_name": "Pseudacris crucifer"},
    "Lithobates catesbeianus": {"id": 1, "common_name": "American Bullfrog", "scientific_name": "Lithobates catesbeianus"},
    "Rana catesbeiana": {"id": 1, "common_name": "American Bullfrog", "scientific_name": "Lithobates catesbeianus"},  # Old name
    "Hyla cinerea": {"id": 3, "common_name": "Green Tree Frog", "scientific_name": "Hyla cinerea"},
    "Pseudacris regilla": {"id": 4, "common_name": "Pacific Tree Frog", "scientific_name": "Pseudacris regilla"},
    "Lithobates sylvaticus": {"id": 5, "common_name": "Wood Frog", "scientific_name": "Lithobates sylvaticus"},
    "Rana sylvatica": {"id": 5, "common_name": "Wood Frog", "scientific_name": "Lithobates sylvaticus"},  # Old name
    "Hyla versicolor": {"id": 6, "common_name": "Gray Tree Frog", "scientific_name": "Hyla versicolor"},
    "Lithobates pipiens": {"id": 7, "common_name": "Northern Leopard Frog", "scientific_name": "Lithobates pipiens"},
    "Rana pipiens": {"id": 7, "common_name": "Northern Leopard Frog", "scientific_name": "Lithobates pipiens"},  # Old name
    "Lithobates clamitans": {"id": 8, "common_name": "Green Frog", "scientific_name": "Lithobates clamitans"},
    "Rana clamitans": {"id": 8, "common_name": "Green Frog", "scientific_name": "Lithobates clamitans"},  # Old name
    "Lithobates palustris": {"id": 9, "common_name": "Pickerel Frog", "scientific_name": "Lithobates palustris"},
    "Pseudacris triseriata": {"id": 10, "common_name": "Western Chorus Frog", "scientific_name": "Pseudacris triseriata"},
    "Acris crepitans": {"id": 11, "common_name": "Northern Cricket Frog", "scientific_name": "Acris crepitans"},
    "Hyla chrysoscelis": {"id": 12, "common_name": "Cope's Gray Treefrog", "scientific_name": "Hyla chrysoscelis"},
    "Hyla gratiosa": {"id": 13, "common_name": "Barking Treefrog", "scientific_name": "Hyla gratiosa"},
    "Hyla squirella": {"id": 14, "common_name": "Squirrel Treefrog", "scientific_name": "Hyla squirella"},
    "Lithobates sphenocephalus": {"id": 15, "common_name": "Southern Leopard Frog", "scientific_name": "Lithobates sphenocephalus"},
    "Lithobates grylio": {"id": 16, "common_name": "Pig Frog", "scientific_name": "Lithobates grylio"},
    "Lithobates heckscheri": {"id": 17, "common_name": "River Frog", "scientific_name": "Lithobates heckscheri"},
    "Lithobates areolatus": {"id": 18, "common_name": "Crawfish Frog", "scientific_name": "Lithobates areolatus"},
    "Lithobates capito": {"id": 19, "common_name": "Gopher Frog", "scientific_name": "Lithobates capito"},
    "Lithobates virgatipes": {"id": 20, "common_name": "Carpenter Frog", "scientific_name": "Lithobates virgatipes"},
    # Tennessee species
    "Anaxyrus americanus": {"id": 21, "common_name": "American Toad", "scientific_name": "Anaxyrus americanus"},
    "Bufo americanus": {"id": 21, "common_name": "American Toad", "scientific_name": "Anaxyrus americanus"},  # Old name
    "Anaxyrus fowleri": {"id": 22, "common_name": "Fowler's Toad", "scientific_name": "Anaxyrus fowleri"},
    "Bufo fowleri": {"id": 22, "common_name": "Fowler's Toad", "scientific_name": "Anaxyrus fowleri"},  # Old name
    "Acris gryllus": {"id": 23, "common_name": "Southern Cricket Frog", "scientific_name": "Acris gryllus"},
    "Dryophytes avivoca": {"id": 24, "common_name": "Bird-voiced Treefrog", "scientific_name": "Dryophytes avivoca"},
    "Hyla avivoca": {"id": 24, "common_name": "Bird-voiced Treefrog", "scientific_name": "Dryophytes avivoca"},  # Old name
    "Pseudacris brachyphona": {"id": 25, "common_name": "Mountain Chorus Frog", "scientific_name": "Pseudacris brachyphona"},
    "Pseudacris feriarum": {"id": 26, "common_name": "Upland Chorus Frog", "scientific_name": "Pseudacris feriarum"},
    "Gastrophryne carolinensis": {"id": 27, "common_name": "Eastern Narrow-mouthed Toad", "scientific_name": "Gastrophryne carolinensis"},
}


class BirdNetAudioClassifier:
    """Audio classifier using BirdNET for frog call identification."""
    
    def __init__(self):
        self.analyzer = None
        self.available = BIRDNET_AVAILABLE
        
        if self.available:
            try:
                self.analyzer = Analyzer()
                logger.info("BirdNET analyzer loaded")
            except Exception as e:
                logger.error("Failed to load BirdNET analyzer: %s", e)
                self.available = False
        else:
            logger.warning("BirdNET not available")
    
    def _find_species_match(self, birdnet_name: str, scientific_name: str) -> Optional[Dict[str, Any]]:
        """Find matching species in our database from BirdNET output."""
        # Try exact match first
        if birdnet_name in SPECIES_MAPPING:
            return SPECIES_MAPPING[birdnet_name]
        
        # Try scientific name (case insensitive)
        sci_lower = scientific_name.lower().strip()
        for key, value in SCIENTIFIC_NAME_MAPPING.items():
            if key.lower() == sci_lower:
                return value
        
        # Try partial matching on common name (extracted from birdnet_name)
        # birdnet_name format is usually "Common Name_Scientific Name"
        common_part = birdnet_name.split("_")[0].lower().strip() if "_" in birdnet_name else birdnet_name.lower().strip()
        
        for key, value in SPECIES_MAPPING.items():
            value_common = value["common_name"].lower()
            # Check if either contains the other
            if common_part in value_common or value_common in common_part:
                return value
            # Also check without "frog" suffix
            common_no_frog = common_part.replace(" frog", "").replace("frog", "").strip()
            value_no_frog = value_common.replace(" frog", "").replace("frog", "").strip()
            if common_no_frog and value_no_frog and (common_no_frog in value_no_frog or value_no_frog in common_no_frog):
                return value
        
        # Try partial matching on scientific name
        for key, value in SCIENTIFIC_NAME_MAPPING.items():
            if key.lower() in sci_lower or sci_lower in key.lower():
                return value
        
        return None
    
    def predict(self, audio_bytes: io.BytesIO) -> List[Dict[str, Any]]:
        """
        Predict frog species from audio using BirdNET.
        
        Args:
            audio_bytes: Audio data as BytesIO object
            
        Returns:
            List of predictions with species info and confidence scores
        """
        if not self.available or not self.analyzer:
            logger.warning("BirdNET not available, returning empty predictions")
            return []
        
        predictions = []
        input_path = None
        tmp_path = None
        
        try:
            audio_bytes.seek(0)
            
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
                input_file.write(audio_bytes.read())
                input_path = input_file.name
            
            tmp_path = input_path.replace('.webm', '.wav')
            
            # Convert audio to WAV format (BirdNET expects 48kHz mono WAV)
            try:
                result = subprocess.run(
                    ['ffmpeg', '-y', '-i', input_path, '-ar', '48000', '-ac', '1', '-f', 'wav', tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    logger.debug("FFmpeg conversion failed, trying librosa")
                    import librosa
                    import soundfile as sf
                    y, sr = librosa.load(input_path, sr=48000, duration=15.0)
                    sf.write(tmp_path, y, sr)
            except Exception as e:
                logger.debug("Audio conversion error: %s, trying librosa fallback", e)
                import librosa
                import soundfile as sf
                audio_bytes.seek(0)
                y, sr = librosa.load(audio_bytes, sr=48000, duration=15.0)
                sf.write(tmp_path, y, sr)
            finally:
                if input_path and os.path.exists(input_path):
                    os.unlink(input_path)
                    input_path = None
            
            recording = Recording(self.analyzer, tmp_path, min_conf=0.01)
            recording.analyze()
            
            logger.debug("BirdNET found %d detections", len(recording.detections))
            
            seen_species = set()
            for detection in recording.detections:
                common_name = detection.get("common_name", "")
                scientific_name = detection.get("scientific_name", "")
                confidence = detection.get("confidence", 0.0)
                full_name = f"{common_name}_{scientific_name}"
                
                species_match = self._find_species_match(full_name, scientific_name)
                
                if species_match and species_match["id"] not in seen_species:
                    seen_species.add(species_match["id"])
                    predictions.append({
                        "species_id": species_match["id"],
                        "common_name": species_match["common_name"],
                        "scientific_name": species_match["scientific_name"],
                        "confidence": float(confidence),
                    })
                elif species_match is None:
                    frog_keywords = ["frog", "peeper", "treefrog", "toad", "bullfrog", "chorus"]
                    if any(kw in common_name.lower() for kw in frog_keywords):
                        logger.debug("Unmatched frog species: %s (%s)", common_name, scientific_name)
                        predictions.append({
                            "species_id": 0,
                            "common_name": common_name,
                            "scientific_name": scientific_name,
                            "confidence": float(confidence),
                        })
            
            predictions.sort(key=lambda x: x["confidence"], reverse=True)
                
        except Exception as e:
            logger.exception("Error during BirdNET prediction: %s", e)
        finally:
            if input_path and os.path.exists(input_path):
                os.unlink(input_path)
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        return predictions[:5]
    
    def get_species_list(self) -> List[Dict[str, Any]]:
        """Get list of frog species we can identify."""
        return list({v["id"]: v for v in SCIENTIFIC_NAME_MAPPING.values()}.values())
