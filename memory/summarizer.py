# Databricks notebook source
# memory/summarizer.py
from tools.lmstudio_client import chat_completion

SYSTEM = """Eres un asistente que resume el estado de la conversación.
Devuelve un resumen breve con los datos persistentes del usuario y sus objetivos.
No repitas saludos. Sé factual y sobrio."""

def update_summary(prev_summary: str, history: list[dict]) -> str:
    # history: [{"role":"user"/"assistant","content":"..."}]
    snippet = "\n".join([f"{h['role']}: {h['content']}" for h in history[-6:]])
    user = f"""Resumen previo:
{prev_summary}

Nuevos mensajes:
{snippet}

Actualiza el resumen en 6-8 líneas como máximo, conservando nombre/rol/preferencias si aparecen."""
    return chat_completion(SYSTEM, user, temperature=0.1, max_tokens=300)