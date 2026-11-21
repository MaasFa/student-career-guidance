import math
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Singleton holders for model and in-memory embedding cache
_MODEL = None
_MODEL_TRIED = False
_EMBEDDING_CACHE: Dict[str, List[float]] = {}


def get_model():
    """Loads the sentence-transformer model once and caches the instance."""
    global _MODEL, _MODEL_TRIED
    if _MODEL is not None:
        return _MODEL
    if _MODEL_TRIED and _MODEL is None:
        return None

    _MODEL_TRIED = True
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model 'all-MiniLM-L6-v2'...")
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer loaded successfully.")
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformer ('all-MiniLM-L6-v2'): {e}. Will use hybrid semantic fallback.")
        _MODEL = None

    return _MODEL


def _fallback_embedding(text: str) -> List[float]:
    """
    Computes a deterministic character-trigram & subword vector for lightweight
    semantic representation when torch/sentence-transformers is unavailable.
    """
    cleaned = text.lower().strip()
    dim = 64
    vec = [0.0] * dim

    # Character n-grams
    ngrams = [cleaned[i:i+3] for i in range(max(1, len(cleaned) - 2))]
    for ng in ngrams:
        idx = hash(ng) % dim
        vec[idx] += 1.0

    # Also include word hashes
    words = cleaned.split()
    for w in words:
        idx = (hash(w) * 7) % dim
        vec[idx] += 2.0

    # Normalize vector to unit length
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def get_embedding(skill_name: str) -> List[float]:
    """
    Retrieves or calculates and caches the embedding vector for a given skill.
    """
    key = skill_name.strip().lower()
    if key in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[key]

    model = get_model()
    if model is not None:
        try:
            # model.encode returns numpy array or list
            vector = model.encode(key, convert_to_numpy=True).tolist()
            _EMBEDDING_CACHE[key] = vector
            return vector
        except Exception as e:
            logger.error(f"Error encoding '{key}' with SentenceTransformer: {e}")

    # Fallback embedding
    vector = _fallback_embedding(key)
    _EMBEDDING_CACHE[key] = vector
    return vector


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two 1D numerical lists."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot / (norm1 * norm2)
    # Clamp to [0.0, 1.0] for similarity measure
    return max(0.0, min(1.0, float(similarity)))


def compute_skill_similarity(skill_a: str, skill_b: str) -> float:
    """
    Computes semantic similarity between two skills, accounting for exact matches,
    domain synonyms, and embedding cosine similarity.
    """
    a = skill_a.strip().lower()
    b = skill_b.strip().lower()

    if a == b:
        return 1.0

    # Direct substring / superset match (e.g. "react" in "react.js" or "rest api" in "restful api")
    if a in b or b in a:
        ratio = min(len(a), len(b)) / max(len(a), len(b))
        if ratio >= 0.6:
            return max(0.85, 0.85 + 0.15 * ratio)

    # Cosine similarity using cached embeddings
    v1 = get_embedding(a)
    v2 = get_embedding(b)
    return cosine_similarity(v1, v2)
