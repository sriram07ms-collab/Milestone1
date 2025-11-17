"""Embedding service for generating vector embeddings"""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings (lazy model load to reduce memory)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize embedding service without loading the model immediately.
        Model loads on first embedding call to minimize startup memory.
        """
        self.model = None
    
    def _ensure_model(self):
        """Load sentence-transformer model if not already loaded"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # Use a lightweight, fast model for embeddings
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Initialized sentence-transformer model: all-MiniLM-L6-v2")
            except ImportError:
                raise ImportError("sentence-transformers is required. Install with: pip install sentence-transformers")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Load model on demand
        try:
            self._ensure_model()
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except ImportError:
            # Fallback: use a simple hash-based approach (not recommended for production)
            logger.warning("Using fallback embedding method (sentence-transformers not installed)")
            return self._simple_embedding(text)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        try:
            self._ensure_model()
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return embeddings.tolist()
        except ImportError:
            return [self._simple_embedding(text) for text in texts]
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding (not recommended for production)"""
        import hashlib
        import struct
        
        # Create a hash-based embedding (384 dimensions to match MiniLM)
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            if len(embedding) >= 384:
                break
            value = struct.unpack('>I', hash_bytes[i:i+4] if len(hash_bytes[i:i+4]) == 4 else hash_bytes[i:i+4] + b'\x00' * (4 - len(hash_bytes[i:i+4])))[0]
            embedding.append((value % 10000) / 10000.0)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]

