# Databricks notebook source
import os
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs): return False
load_dotenv()

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "meta-llama-3-8b-instruct")
EMBED_MODEL = os.getenv("EMBED_MODEL", "thenlper/gte-base")

TOP_K = int(os.getenv("TOP_K", "4"))
MAX_CTX_CHARS = int(os.getenv("MAX_CTX_CHARS", "4500"))

FAISS_PATH = os.getenv("FAISS_PATH", "data/processed/faiss.index")
META_PATH  = os.getenv("META_PATH",  "data/processed/meta.json")
CORPUS_PATH = os.getenv("CORPUS_PATH", "data/processed/corpus.jsonl")

INDEX_READONLY = os.getenv("INDEX_READONLY", "true").lower() == "true"
INDEX_AUTORELOAD_SEC = int(os.getenv("INDEX_AUTORELOAD_SEC", "0"))

# === nuevo: seguridad
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true"
API_TOKENS = {t.strip() for t in os.getenv("API_TOKENS", "").split(",") if t.strip()}

# === nuevo: conversación/memoria
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "120"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "8"))
MEMORY_SUMMARY_MAX_CHARS = int(os.getenv("MEMORY_SUMMARY_MAX_CHARS", "1200"))
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "America/Santiago")

# (Fase 2) Databricks
DBR_SERVER_HOSTNAME = os.getenv("DBR_SERVER_HOSTNAME", "")
DBR_HTTP_PATH = os.getenv("DBR_HTTP_PATH", "")
DBR_TOKEN = os.getenv("DBR_TOKEN", "")