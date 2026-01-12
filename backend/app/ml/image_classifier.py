"""Fallback image classifier for frog species identification using CNN."""

import io
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
FROG_SPECIES = [
    {"id": 1, "common_name": "American Bullfrog", "scientific_name": "Lithobates catesbeianus"},
    {"id": 2, "common_name": "Spring Peeper", "scientific_name": "Pseudacris crucifer"},
    {"id": 3, "common_name": "Green Tree Frog", "scientific_name": "Hyla cinerea"},
    {"id": 4, "common_name": "Pacific Tree Frog", "scientific_name": "Pseudacris regilla"},
    {"id": 5, "common_name": "Wood Frog", "scientific_name": "Lithobates sylvaticus"},
    {"id": 6, "common_name": "Gray Tree Frog", "scientific_name": "Hyla versicolor"},
    {"id": 7, "common_name": "Leopard Frog", "scientific_name": "Lithobates pipiens"},
    {"id": 8, "common_name": "Green Frog", "scientific_name": "Lithobates clamitans"},
    {"id": 9, "common_name": "Pickerel Frog", "scientific_name": "Lithobates palustris"},
    {"id": 10, "common_name": "Chorus Frog", "scientific_name": "Pseudacris triseriata"},
    {"id": 11, "common_name": "Cricket Frog", "scientific_name": "Acris crepitans"},
    {"id": 12, "common_name": "Cope's Gray Treefrog", "scientific_name": "Hyla chrysoscelis"},
    {"id": 13, "common_name": "Barking Treefrog", "scientific_name": "Hyla gratiosa"},
    {"id": 14, "common_name": "Squirrel Treefrog", "scientific_name": "Hyla squirella"},
    {"id": 15, "common_name": "Southern Leopard Frog", "scientific_name": "Lithobates sphenocephalus"},
    {"id": 16, "common_name": "Pig Frog", "scientific_name": "Lithobates grylio"},
    {"id": 17, "common_name": "River Frog", "scientific_name": "Lithobates heckscheri"},
    {"id": 18, "common_name": "Crawfish Frog", "scientific_name": "Lithobates areolatus"},
    {"id": 19, "common_name": "Gopher Frog", "scientific_name": "Lithobates capito"},
    {"id": 20, "common_name": "Carpenter Frog", "scientific_name": "Lithobates virgatipes"},
]


class ImageCNN(nn.Module):
    """CNN model for image classification."""
    
    def __init__(self, num_classes: int = 20):
        super().__init__()
        
        # Convolutional backbone
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            
            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            # Block 4
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            # Block 5
            nn.Conv2d(256, 512, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
        )
        
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.5)
        
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = self.classifier(x)
        return x


class ImageClassifier:
    """Fallback image classifier using CNN."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ImageCNN(num_classes=len(FROG_SPECIES))
        self.model.to(self.device)
        self.model.eval()
        
        model_path = model_path or settings.image_model_path
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            logger.info("Loaded image model from %s", model_path)
        else:
            logger.warning("No image model found, using untrained model")
        
        self.image_size = 224
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
    
    def _preprocess_image(self, image_bytes: io.BytesIO) -> torch.Tensor:
        """Load and preprocess image from bytes."""
        try:
            image_bytes.seek(0)
            img = Image.open(image_bytes).convert("RGB")
            img = img.resize((self.image_size, self.image_size), Image.Resampling.LANCZOS)
            
            img_array = np.array(img, dtype=np.float32) / 255.0
            for i in range(3):
                img_array[:, :, i] = (img_array[:, :, i] - self.mean[i]) / self.std[i]
            
            return torch.from_numpy(img_array).permute(2, 0, 1).float()
        except Exception as e:
            logger.debug("Error preprocessing image: %s", e)
            return torch.zeros(3, self.image_size, self.image_size)
    
    def predict(self, image_bytes: io.BytesIO) -> List[Dict[str, Any]]:
        """
        Predict frog species from image.
        
        Args:
            image_bytes: Image data as BytesIO object
            
        Returns:
            List of predictions with species info and confidence scores
        """
        # Preprocess image
        img_tensor = self._preprocess_image(image_bytes)
        img_tensor = img_tensor.unsqueeze(0).to(self.device)  # Add batch dim
        
        # Run inference
        with torch.no_grad():
            logits = self.model(img_tensor)
            probs = F.softmax(logits, dim=1)
        
        # Get top predictions
        probs_np = probs.cpu().numpy()[0]
        top_indices = np.argsort(probs_np)[::-1][:5]
        
        predictions = []
        for idx in top_indices:
            species = FROG_SPECIES[idx]
            predictions.append({
                "species_id": species["id"],
                "common_name": species["common_name"],
                "scientific_name": species["scientific_name"],
                "confidence": float(probs_np[idx]),
            })
        
        return predictions
    
    def get_species_list(self) -> List[Dict[str, Any]]:
        """Get list of all identifiable species."""
        return FROG_SPECIES
