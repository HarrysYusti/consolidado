# Databricks notebook source
from tools.embeddings import Embedder
from .retriever import Retriever
import config

class RagPipeline:
    def __init__(self):
        self.embedder = Embedder(config.EMBED_MODEL)
        self.retriever = Retriever()

    def build_context(self, query: str, memory_summary: str, top_k: int):
        q_emb = self.embedder.encode([query])
        hits = self.retriever.search(q_emb, top_k)
        chunks, total = [], 0
        if memory_summary:
            chunks.append(f"[MEMORIA BREVE]\n{memory_summary}\n")
        for h in hits:
            t = h["text"]
            if total + len(t) > config.MAX_CTX_CHARS: break
            chunks.append(t); total += len(t)
        return "\n---\n".join(chunks), hits