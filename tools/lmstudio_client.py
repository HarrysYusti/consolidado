# Databricks notebook source
import requests, config

def chat_completion(system: str, user: str, temperature=0.2, max_tokens=600):
    payload = {
        "model": config.LM_STUDIO_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    r = requests.post(config.LM_STUDIO_URL, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # API LM Studio: respuesta típica estilo OpenAI
    return data["choices"][0]["message"]["content"]
