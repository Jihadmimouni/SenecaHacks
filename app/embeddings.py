"""
Embeddings module for text vectorization using sentence-transformers.
Supports both Arabic and English text.
"""

from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Get or load the sentence transformer model.
    Uses LRU cache to avoid reloading the model.
    
    Args:
        model_name (str): Name of the sentence transformer model
        
    Returns:
        SentenceTransformer: Loaded model instance
    """
    return SentenceTransformer(model_name)

def get_embedding(text: str) -> np.ndarray:
    """
    Convert text into a vector embedding.
    Supports both Arabic and English text.
    
    Args:
        text (str): Input text to convert to embedding
        
    Returns:
        np.ndarray: Vector embedding of the input text
    """
    # Clean and preprocess text
    text = text.strip()
    if not text:
        raise ValueError("Empty text cannot be embedded")
    
    # Get model instance (cached)
    model = get_model()
    
    # Generate embedding
    embedding = model.encode(text, 
                           normalize_embeddings=True,  # L2 normalization
                           convert_to_numpy=True)
    
    return embedding

def get_embeddings_batch(texts: list[str]) -> np.ndarray:
    """
    Convert multiple texts into vector embeddings in batch.
    More efficient than processing one at a time.
    
    Args:
        texts (list[str]): List of input texts
        
    Returns:
        np.ndarray: Matrix of embeddings, shape (n_texts, embedding_dim)
    """
    # Clean texts
    texts = [text.strip() for text in texts]
    if not texts:
        raise ValueError("Empty text list")
    if any(not text for text in texts):
        raise ValueError("Some texts are empty")
    
    # Get model instance (cached)
    model = get_model()
    
    # Generate embeddings in batch
    embeddings = model.encode(texts,
                            normalize_embeddings=True,
                            convert_to_numpy=True,
                            batch_size=32)  # Adjust based on your GPU memory
    
    return embeddings
