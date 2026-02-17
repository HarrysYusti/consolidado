# Databricks notebook source
import json, os, time
import faiss
import numpy as np
import config

class Retriever:
    def __init__(self, index_path=config.FAISS_PATH, meta_path=config.META_PATH):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index_mtime = None
        self.index = None
        self.items = None
        self._load_all()

    def _load_all(self):
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            raise FileNotFoundError("FAISS o meta.json no encontrados.")
        self.index = faiss.read_index(self.index_path)
        self.index_mtime = os.path.getmtime(self.index_path)
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.items = meta["items"]
        # Validación suave de compatibilidad
        meta_info = meta.get("meta", {})
        embed_model_built = meta_info.get("embed_model")
        if embed_model_built and embed_model_built != config.EMBED_MODEL:
            raise RuntimeError(f"El índice fue construido con {embed_model_built} y el runtime usa {config.EMBED_MODEL}.")
        self.vector_dim = meta_info.get("vector_dim")

    def maybe_reload(self):
        if config.INDEX_AUTORELOAD_SEC <= 0:
            return
        try:
            mtime = os.path.getmtime(self.index_path)
            if mtime > (self.index_mtime or 0):
                self._load_all()
        except Exception:
            pass

    def search(self, query_emb: np.ndarray, top_k: int):
        self.maybe_reload()
        D, I = self.index.search(query_emb.astype("float32"), top_k)
        results = []
        for rank, (idx, score) in enumerate(zip(I[0], D[0])):
            if idx < 0: 
                continue
            item = self.items[idx]
            results.append({"rank": rank, "score": float(score), **item})
        return results
