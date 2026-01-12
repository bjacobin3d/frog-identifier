"""Fallback audio classifier for frog call identification using mel spectrograms."""

import io
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

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


class AudioCNN(nn.Module):
    """CNN model for audio classification using mel spectrograms."""
    
    def __init__(self, num_classes: int = 20):
        super().__init__()
        
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(256)
        self.conv4 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(512)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(0.5)
        
        self.fc1 = nn.Linear(512, 256)
        self.fc2 = nn.Linear(256, num_classes)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch, 1, mel_bins, time_frames)
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        
        x = self.adaptive_pool(x)
        x = x.view(x.size(0), -1)
        
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        
        return x


class AudioClassifier:
    """Fallback audio classifier using CNN on mel spectrograms."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AudioCNN(num_classes=len(FROG_SPECIES))
        self.model.to(self.device)
        self.model.eval()
        
        model_path = model_path or settings.audio_model_path
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            logger.info("Loaded audio model from %s", model_path)
        else:
            logger.warning("No audio model found, using untrained model")
        
        self.sample_rate = 22050
        self.n_mels = 128
        self.n_fft = 2048
        self.hop_length = 512
        self.duration = 5.0
    
    def _load_audio(self, audio_bytes: io.BytesIO) -> np.ndarray:
        """Load audio from bytes and convert to numpy array."""
        try:
            import librosa
            
            audio_bytes.seek(0)
            y, _ = librosa.load(audio_bytes, sr=self.sample_rate, duration=self.duration)
            
            target_length = int(self.sample_rate * self.duration)
            if len(y) < target_length:
                y = np.pad(y, (0, target_length - len(y)))
            else:
                y = y[:target_length]
            
            return y
        except Exception as e:
            logger.debug("Error loading audio: %s", e)
            return np.zeros(int(self.sample_rate * self.duration))
    
    def _compute_mel_spectrogram(self, audio: np.ndarray) -> np.ndarray:
        """Compute mel spectrogram from audio waveform."""
        try:
            import librosa
            
            mel_spec = librosa.feature.melspectrogram(
                y=audio,
                sr=self.sample_rate,
                n_mels=self.n_mels,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
            )
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / (mel_spec_db.std() + 1e-8)
            
            return mel_spec_db
        except Exception as e:
            logger.debug("Error computing mel spectrogram: %s", e)
            return np.zeros((self.n_mels, 216))
    
    def predict(self, audio_bytes: io.BytesIO) -> List[Dict[str, Any]]:
        """
        Predict frog species from audio.
        
        Args:
            audio_bytes: Audio data as BytesIO object
            
        Returns:
            List of predictions with species info and confidence scores
        """
        # Load and process audio
        audio = self._load_audio(audio_bytes)
        mel_spec = self._compute_mel_spectrogram(audio)
        
        # Convert to tensor
        mel_tensor = torch.from_numpy(mel_spec).float()
        mel_tensor = mel_tensor.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
        mel_tensor = mel_tensor.to(self.device)
        
        # Run inference
        with torch.no_grad():
            logits = self.model(mel_tensor)
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
