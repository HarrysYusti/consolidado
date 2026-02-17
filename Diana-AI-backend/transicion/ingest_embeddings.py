#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper script to build FAISS embeddings from a prepared corpus.jsonl.

Prereqs (install on your local machine with internet):
    pip install sentence-transformers faiss-cpu numpy

Usage:
    python ingest_embeddings.py --corpus ./processed/corpus.jsonl \
                                --index ./processed/faiss.index \
                                --meta  ./processed/meta.json \
                                --model thenlper/gte-base
"""
import os, json, argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def load_corpus(corpus_path):
    items = []
    texts = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            items.append(obj)
            texts.append(obj["text"])
    return items, texts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="corpus.jsonl", help="Path to corpus.jsonl")
    parser.add_argument("--index", default="faiss.index", help="Where to save FAISS index")
    parser.add_argument("--meta",  default="meta.json", help="Path to meta.json to update (optional)")
    parser.add_argument("--model", default="thenlper/gte-base", help="Embedding model for SentenceTransformers")
    args = parser.parse_args()

    items, texts = load_corpus(args.corpus)
    if not items:
        raise ValueError("No items found in corpus")

    print(f"Loaded {len(items)} items. Embedding with model: {args.model}")
    model = SentenceTransformer(args.model)
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine via normalized dot product
    index.add(embeddings)
    faiss.write_index(index, args.index)
    print(f"FAISS index saved to: {args.index}")

    # Optionally update meta.json with vector_dim and count
    try:
        with open(args.meta, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception:
        meta = {"meta": {}}
    meta.setdefault("meta", {})
    meta["meta"]["vector_dim"] = int(dim)
    meta["meta"]["total_items"] = int(len(items))
    with open(args.meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Meta updated at: {args.meta}")

if __name__ == "__main__":
    main()
