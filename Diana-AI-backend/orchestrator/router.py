# Databricks notebook source
from agents.chat_agent import ChatAgent
from memory.store import STORE
from memory.summarizer import update_summary
from faq.builtin import try_answer
import re

WHOAMI_RE = re.compile(r"\b(me llamo|soy)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ][\wÁÉÍÓÚáéíóúñÑ]+)", re.I)

class Router:
    def __init__(self):
        self.chat = ChatAgent()

    def route(self, question: str, sid: str):
        # Extrae whoami si el usuario lo dice
        m = WHOAMI_RE.search(question)
        if m: 
            name = m.group(2)
            STORE.append(sid, "note", f"whoami={name}")

        # Contexto sesión
        history = STORE.get_history(sid)
        summary = STORE.get_summary(sid)
        whoami = next((h["content"].split("=",1)[1] for h in history if h["role"]=="note" and h["content"].startswith("whoami=")), None)
        session_ctx = {"whoami": whoami}

        # 1) Small-talk shortcut
        st = try_answer(question, session_ctx)
        if st == "__CLEAR__":
            STORE.clear(sid)
            return {"answer": "Conversación borrada 👌", "references": []}
        if st:
            STORE.append(sid, "user", question)
            STORE.append(sid, "assistant", st)
            new_summary = update_summary(summary, STORE.get_history(sid))
            STORE.set_summary(sid, new_summary)
            return {"answer": st, "references": []}

        # 2) RAG normal
        STORE.append(sid, "user", question)
        result = self.chat.answer_with_memory(question, memory_summary=summary)
        STORE.append(sid, "assistant", result["answer"])

        # 3) Actualiza resumen
        new_summary = update_summary(summary, STORE.get_history(sid))
        STORE.set_summary(sid, new_summary)
        return result