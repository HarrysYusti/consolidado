# Databricks notebook source
from sentence_transformers import SentenceTransformer
import threading
import numpy as np
import config

_model = None
_lock = threading.Lock()

def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer(config.EMBED_MODEL)
    return _model

class Embedder:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or config.EMBED_MODEL

    def encode(self, texts: list[str]) -> np.ndarray:
        # Solo queries en runtime
        m = _get_model()
        return m.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
