# Databricks notebook source
# memory/store.py
import time, threading
from collections import defaultdict, deque
import config

class InMemoryStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.history = defaultdict(lambda: deque(maxlen=config.MAX_HISTORY_TURNS))
        self.summary = {}      # sid -> str
        self.expiry = {}       # sid -> epoch seconds

    def _check_expired(self, sid: str):
        exp = self.expiry.get(sid)
        if exp and time.time() > exp:
            self.clear(sid)

    def append(self, sid: str, role: str, content: str):
        with self.lock:
            self._check_expired(sid)
            self.history[sid].append({"role": role, "content": content})
            self.expiry[sid] = time.time() + config.SESSION_TTL_MINUTES*60

    def get_history(self, sid: str):
        with self.lock:
            self._check_expired(sid)
            return list(self.history[sid])

    def set_summary(self, sid: str, text: str):
        with self.lock:
            self.summary[sid] = text[:config.MEMORY_SUMMARY_MAX_CHARS]
            self.expiry[sid] = time.time() + config.SESSION_TTL_MINUTES*60

    def get_summary(self, sid: str) -> str:
        with self.lock:
            self._check_expired(sid)
            return self.summary.get(sid, "")

    def clear(self, sid: str):
        with self.lock:
            self.history.pop(sid, None)
            self.summary.pop(sid, None)
            self.expiry.pop(sid, None)

STORE = InMemoryStore()