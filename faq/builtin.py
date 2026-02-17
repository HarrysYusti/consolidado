# Databricks notebook source
# faq/builtin.py
import re, datetime, zoneinfo
import config

RULES = [
    (re.compile(r"^(hola|buen[oa]s|hey|hi)\b", re.I), lambda ctx: "¡Hola! Soy DIANA, tu asistente de datos y ayuda interna."),
    (re.compile(r"qu[ié]n eres|tu nombre|qu[ié]n te cre[oó]|\bqué eres\b", re.I), lambda ctx: "Soy DIANA, un asistente con RAG sobre Glosario/Accesos/FAQ y conexión a Databricks (cuando está habilitado SQL)."),
    (re.compile(r"qu[ié]n soy|c[oó]mo me llamo", re.I), lambda ctx: ctx.get("whoami") or "Aún no me has dicho tu nombre 😉"),
    (re.compile(r"hora|fech[a]|\bqué día\b", re.I), lambda ctx: _now_str()),
    (re.compile(r"limpia(r)? (chat|conversaci[oó]n)|^reset\b|^borrar\b", re.I), lambda ctx: "__CLEAR__"),
    (re.compile(r"ayuda|qué puedes hacer|help", re.I), lambda ctx: "Puedo responder glosario/FAQ/accesos usando RAG. También puedo convertir preguntas a SQL en Databricks (si está habilitado).")
]

def _now_str():
    tz = zoneinfo.ZoneInfo(config.DEFAULT_TIMEZONE)
    now = datetime.datetime.now(tz)
    return f"Son las {now:%H:%M} del {now:%d-%m-%Y} ({config.DEFAULT_TIMEZONE})."

def try_answer(text: str, session_ctx: dict) -> str | None:
    for pat, fn in RULES:
        if pat.search(text):
            ans = fn(session_ctx)
            return ans
    return None