"""HuggingFace CLIP-based image classifier for frog species identification."""

import io
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

try:
    from transformers import pipeline
    from PIL import Image
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not installed")


# Our frog species with descriptions for better matching
FROG_SPECIES = [
    {"id": 1, "common_name": "American Bullfrog", "scientific_name": "Lithobates catesbeianus",
     "labels": ["american bullfrog", "bullfrog", "large green frog", "Lithobates catesbeianus"]},
    {"id": 2, "common_name": "Spring Peeper", "scientific_name": "Pseudacris crucifer",
     "labels": ["spring peeper", "small brown frog with X on back", "Pseudacris crucifer", "tiny tree frog"]},
    {"id": 3, "common_name": "Green Tree Frog", "scientific_name": "Hyla cinerea",
     "labels": ["green tree frog", "bright green frog", "Hyla cinerea", "american green treefrog"]},
    {"id": 4, "common_name": "Pacific Tree Frog", "scientific_name": "Pseudacris regilla",
     "labels": ["pacific tree frog", "pacific chorus frog", "Pseudacris regilla", "small green or brown frog"]},
    {"id": 5, "common_name": "Wood Frog", "scientific_name": "Lithobates sylvaticus",
     "labels": ["wood frog", "frog with dark mask", "Lithobates sylvaticus", "brown frog with eye mask"]},
    {"id": 6, "common_name": "Gray Tree Frog", "scientific_name": "Hyla versicolor",
     "labels": ["gray tree frog", "grey treefrog", "Hyla versicolor", "warty gray frog"]},
    {"id": 7, "common_name": "Northern Leopard Frog", "scientific_name": "Lithobates pipiens",
     "labels": ["leopard frog", "spotted frog", "Lithobates pipiens", "green frog with dark spots"]},
    {"id": 8, "common_name": "Green Frog", "scientific_name": "Lithobates clamitans",
     "labels": ["green frog", "bronze frog", "Lithobates clamitans", "frog with ridges on back"]},
    {"id": 9, "common_name": "Pickerel Frog", "scientific_name": "Lithobates palustris",
     "labels": ["pickerel frog", "frog with rectangular spots", "Lithobates palustris"]},
    {"id": 10, "common_name": "Western Chorus Frog", "scientific_name": "Pseudacris triseriata",
     "labels": ["chorus frog", "striped frog", "Pseudacris triseriata", "small frog with stripes"]},
    {"id": 11, "common_name": "Northern Cricket Frog", "scientific_name": "Acris crepitans",
     "labels": ["cricket frog", "warty small frog", "Acris crepitans", "tiny brown frog"]},
    {"id": 12, "common_name": "Cope's Gray Treefrog", "scientific_name": "Hyla chrysoscelis",
     "labels": ["cope's gray treefrog", "gray tree frog", "Hyla chrysoscelis"]},
    {"id": 13, "common_name": "Barking Treefrog", "scientific_name": "Hyla gratiosa",
     "labels": ["barking treefrog", "large green treefrog with spots", "Hyla gratiosa"]},
    {"id": 14, "common_name": "Squirrel Treefrog", "scientific_name": "Hyla squirella",
     "labels": ["squirrel treefrog", "small variable colored treefrog", "Hyla squirella"]},
    {"id": 15, "common_name": "Southern Leopard Frog", "scientific_name": "Lithobates sphenocephalus",
     "labels": ["southern leopard frog", "spotted frog pointed snout", "Lithobates sphenocephalus"]},
    {"id": 16, "common_name": "Pig Frog", "scientific_name": "Lithobates grylio",
     "labels": ["pig frog", "large aquatic frog", "Lithobates grylio"]},
    {"id": 17, "common_name": "River Frog", "scientific_name": "Lithobates heckscheri",
     "labels": ["river frog", "large dark frog", "Lithobates heckscheri"]},
    {"id": 18, "common_name": "Crawfish Frog", "scientific_name": "Lithobates areolatus",
     "labels": ["crawfish frog", "stocky spotted frog", "Lithobates areolatus"]},
    {"id": 19, "common_name": "Gopher Frog", "scientific_name": "Lithobates capito",
     "labels": ["gopher frog", "robust spotted frog", "Lithobates capito"]},
    {"id": 20, "common_name": "Carpenter Frog", "scientific_name": "Lithobates virgatipes",
     "labels": ["carpenter frog", "striped frog", "Lithobates virgatipes"]},
    # Tennessee species
    {"id": 21, "common_name": "American Toad", "scientific_name": "Anaxyrus americanus",
     "labels": ["american toad", "common toad", "warty brown toad", "Anaxyrus americanus", "Bufo americanus"]},
    {"id": 22, "common_name": "Fowler's Toad", "scientific_name": "Anaxyrus fowleri",
     "labels": ["fowler's toad", "small toad", "gray toad", "Anaxyrus fowleri", "Bufo fowleri"]},
    {"id": 23, "common_name": "Southern Cricket Frog", "scientific_name": "Acris gryllus",
     "labels": ["southern cricket frog", "small warty frog", "Acris gryllus"]},
    {"id": 24, "common_name": "Bird-voiced Treefrog", "scientific_name": "Dryophytes avivoca",
     "labels": ["bird-voiced treefrog", "gray treefrog yellow thigh", "Dryophytes avivoca", "Hyla avivoca"]},
    {"id": 25, "common_name": "Mountain Chorus Frog", "scientific_name": "Pseudacris brachyphona",
     "labels": ["mountain chorus frog", "small frog dark triangle", "Pseudacris brachyphona"]},
    {"id": 26, "common_name": "Upland Chorus Frog", "scientific_name": "Pseudacris feriarum",
     "labels": ["upland chorus frog", "striped chorus frog", "Pseudacris feriarum"]},
    {"id": 27, "common_name": "Eastern Narrow-mouthed Toad", "scientific_name": "Gastrophryne carolinensis",
     "labels": ["narrow-mouthed toad", "pointed snout toad", "small plump toad", "Gastrophryne carolinensis"]},
]

# Create flat list of all labels to species mapping
LABEL_TO_SPECIES = {}
for species in FROG_SPECIES:
    for label in species["labels"]:
        LABEL_TO_SPECIES[label] = species


class HuggingFaceImageClassifier:
    """Image classifier using CLIP zero-shot classification."""
    
    def __init__(self):
        self.available = TRANSFORMERS_AVAILABLE
        self.classifier = None
        self.labels: List[str] = []
        
        if self.available:
            try:
                logger.info("Loading CLIP model...")
                self.classifier = pipeline(
                    "zero-shot-image-classification",
                    model="openai/clip-vit-base-patch32",
                    device=-1
                )
                self.labels = list(LABEL_TO_SPECIES.keys())
                logger.info("HuggingFace classifier loaded with %d labels", len(self.labels))
            except Exception as e:
                logger.error("Failed to load HuggingFace classifier: %s", e)
                self.available = False
        else:
            logger.warning("HuggingFace transformers not available")
    
    def predict(self, image_bytes: io.BytesIO) -> List[Dict[str, Any]]:
        """
        Predict frog species from image using CLIP zero-shot classification.
        
        Args:
            image_bytes: Image data as BytesIO object
            
        Returns:
            List of predictions with species info and confidence scores
        """
        if not self.available or not self.classifier:
            logger.warning("HuggingFace classifier not available")
            return []
        
        predictions: List[Dict[str, Any]] = []
        
        try:
            image_bytes.seek(0)
            image = Image.open(image_bytes).convert("RGB")
            
            results = self.classifier(
                image,
                candidate_labels=self.labels,
                hypothesis_template="a photo of a {}"
            )
            
            logger.debug("CLIP found %d results", len(results))
            
            # Group results by species and take the best score for each
            species_scores: Dict[int, Dict[str, Any]] = {}
            for result in results:
                label = result["label"]
                score = result["score"]
                
                if label in LABEL_TO_SPECIES:
                    species = LABEL_TO_SPECIES[label]
                    species_id = species["id"]
                    
                    if species_id not in species_scores or score > species_scores[species_id]["confidence"]:
                        species_scores[species_id] = {
                            "species_id": species_id,
                            "common_name": species["common_name"],
                            "scientific_name": species["scientific_name"],
                            "confidence": float(score),
                        }
            
            predictions = sorted(
                species_scores.values(),
                key=lambda x: x["confidence"],
                reverse=True
            )[:5]
            
        except Exception as e:
            logger.exception("Error during image classification: %s", e)
        
        return predictions
    
    def get_species_list(self) -> List[Dict[str, Any]]:
        """Get list of frog species we can identify."""
        return [{"id": s["id"], "common_name": s["common_name"], "scientific_name": s["scientific_name"]} 
                for s in FROG_SPECIES]
