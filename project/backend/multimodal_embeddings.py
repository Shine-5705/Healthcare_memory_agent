"""
Multimodal Embeddings Generator for Healthcare Data

This module provides embedding generation for multiple data modalities:
- Images (skin conditions, medical images) using CLIP
- Audio (cough analysis, respiratory sounds) using Wav2Vec2
- Cross-modal search capabilities (text-to-image, image-to-text)

Features:
- CLIP ViT-B/32 for vision-language embeddings (512 dimensions)
- Wav2Vec2 for audio embeddings (768 dimensions)
- Unified embedding space for cross-modal retrieval
- GPU acceleration when available
"""

import torch
import numpy as np
from typing import Union, List, Tuple, Optional
from PIL import Image
import io
import base64
import logging
import librosa
import soundfile as sf
from transformers import CLIPProcessor, CLIPModel, Wav2Vec2Processor, Wav2Vec2Model

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultimodalEmbeddingGenerator:
    """
    Generate embeddings for images, audio, and text using state-of-the-art models
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading models multiple times"""
        if cls._instance is None:
            cls._instance = super(MultimodalEmbeddingGenerator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize embedding models"""
        if self._initialized:
            return
        
        logger.info("🤖 Initializing Multimodal Embedding Generator...")
        
        # Check for GPU availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"💻 Using device: {self.device}")
        
        # Initialize CLIP for image-text embeddings
        try:
            logger.info("📸 Loading CLIP model (openai/clip-vit-base-patch32)...")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_dim = 512
            logger.info("✅ CLIP model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load CLIP model: {e}")
            self.clip_model = None
            self.clip_processor = None
        
        # Initialize Wav2Vec2 for audio embeddings
        try:
            logger.info("🎵 Loading Wav2Vec2 model (facebook/wav2vec2-base)...")
            self.audio_model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base").to(self.device)
            self.audio_processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
            self.audio_dim = 768
            logger.info("✅ Wav2Vec2 model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Wav2Vec2 model: {e}")
            self.audio_model = None
            self.audio_processor = None
        
        self._initialized = True
        logger.info("✅ Multimodal Embedding Generator initialized")
    
    def generate_image_embedding(self, image: Union[Image.Image, str, bytes]) -> Optional[np.ndarray]:
        """
        Generate 512-dimensional embedding from image using CLIP
        
        Args:
            image: PIL Image, base64 string, or bytes
            
        Returns:
            numpy array of shape (512,) or None if failed
        """
        if self.clip_model is None:
            logger.error("CLIP model not available")
            return None
        
        try:
            # Convert input to PIL Image
            if isinstance(image, str):
                # Handle base64 encoded images
                if image.startswith('data:image'):
                    image = image.split(',')[1]
                image_bytes = base64.b64decode(image)
                image = Image.open(io.BytesIO(image_bytes))
            elif isinstance(image, bytes):
                image = Image.open(io.BytesIO(image))
            
            # Ensure RGB format
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Process image through CLIP
            inputs = self.clip_processor(images=image, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                # Normalize embedding
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embedding = image_features.cpu().numpy()[0]
            
            logger.debug(f"Generated image embedding: shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating image embedding: {e}")
            return None
    
    def generate_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate 512-dimensional embedding from text using CLIP
        (in same space as images for cross-modal search)
        
        Args:
            text: Text description
            
        Returns:
            numpy array of shape (512,) or None if failed
        """
        if self.clip_model is None:
            logger.error("CLIP model not available")
            return None
        
        try:
            # Process text through CLIP
            inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                text_features = self.clip_model.get_text_features(**inputs)
                # Normalize embedding
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embedding = text_features.cpu().numpy()[0]
            
            logger.debug(f"Generated text embedding: shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            return None
    
    def generate_audio_embedding(self, audio_file: Union[str, bytes, np.ndarray]) -> Optional[np.ndarray]:
        """
        Generate 768-dimensional embedding from audio using Wav2Vec2
        
        Args:
            audio_file: Path to audio file, audio bytes, or numpy array
            
        Returns:
            numpy array of shape (768,) or None if failed
        """
        if self.audio_model is None:
            logger.error("Wav2Vec2 model not available")
            return None
        
        try:
            # Load audio
            if isinstance(audio_file, str):
                # Load from file path
                audio, sr = librosa.load(audio_file, sr=16000)
            elif isinstance(audio_file, bytes):
                # Load from bytes
                audio, sr = sf.read(io.BytesIO(audio_file))
                # Resample to 16kHz if needed
                if sr != 16000:
                    audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                    sr = 16000
            elif isinstance(audio_file, np.ndarray):
                audio = audio_file
                sr = 16000
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_file)}")
            
            # Ensure mono
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
            
            # Process audio through Wav2Vec2
            inputs = self.audio_processor(
                audio,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                outputs = self.audio_model(**inputs)
                # Take mean pooling over time dimension
                audio_features = outputs.last_hidden_state.mean(dim=1)
                # Normalize embedding
                audio_features = audio_features / audio_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy
            embedding = audio_features.cpu().numpy()[0]
            
            logger.debug(f"Generated audio embedding: shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating audio embedding: {e}")
            return None
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Normalize vectors
            emb1_norm = embedding1 / np.linalg.norm(embedding1)
            emb2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Cosine similarity
            similarity = np.dot(emb1_norm, emb2_norm)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def batch_generate_image_embeddings(self, images: List[Union[Image.Image, str, bytes]]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple images efficiently
        
        Args:
            images: List of images
            
        Returns:
            List of embedding arrays
        """
        embeddings = []
        for img in images:
            emb = self.generate_image_embedding(img)
            if emb is not None:
                embeddings.append(emb)
        
        return embeddings
    
    def get_embedding_dimensions(self) -> dict:
        """
        Get dimensions of each embedding type
        
        Returns:
            Dictionary with embedding dimensions
        """
        return {
            "image": self.clip_dim if self.clip_model else None,
            "text": self.clip_dim if self.clip_model else None,
            "audio": self.audio_dim if self.audio_model else None
        }
    
    def is_available(self) -> dict:
        """
        Check which models are available
        
        Returns:
            Dictionary indicating model availability
        """
        return {
            "clip": self.clip_model is not None,
            "wav2vec2": self.audio_model is not None,
            "gpu": torch.cuda.is_available()
        }


# Global instance for easy access
_embedding_generator = None

def get_embedding_generator() -> MultimodalEmbeddingGenerator:
    """
    Get or create the global embedding generator instance
    
    Returns:
        MultimodalEmbeddingGenerator instance
    """
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = MultimodalEmbeddingGenerator()
    return _embedding_generator


# Convenience functions
def embed_image(image: Union[Image.Image, str, bytes]) -> Optional[np.ndarray]:
    """Generate image embedding"""
    return get_embedding_generator().generate_image_embedding(image)


def embed_text(text: str) -> Optional[np.ndarray]:
    """Generate text embedding (CLIP space)"""
    return get_embedding_generator().generate_text_embedding(text)


def embed_audio(audio: Union[str, bytes, np.ndarray]) -> Optional[np.ndarray]:
    """Generate audio embedding"""
    return get_embedding_generator().generate_audio_embedding(audio)


if __name__ == "__main__":
    # Test the embedding generator
    print("Testing Multimodal Embedding Generator...")
    
    generator = get_embedding_generator()
    print(f"\nModel availability: {generator.is_available()}")
    print(f"Embedding dimensions: {generator.get_embedding_dimensions()}")
    
    # Test text embedding
    text_emb = generator.generate_text_embedding("A red rash on the skin")
    if text_emb is not None:
        print(f"✅ Text embedding: shape {text_emb.shape}")
    
    # Test image embedding (create a dummy image)
    from PIL import Image
    dummy_image = Image.new('RGB', (224, 224), color='red')
    img_emb = generator.generate_image_embedding(dummy_image)
    if img_emb is not None:
        print(f"✅ Image embedding: shape {img_emb.shape}")
    
    # Test cross-modal similarity
    if text_emb is not None and img_emb is not None:
        similarity = generator.compute_similarity(text_emb, img_emb)
        print(f"✅ Cross-modal similarity: {similarity:.4f}")
    
    print("\n✅ Multimodal Embedding Generator test completed!")
