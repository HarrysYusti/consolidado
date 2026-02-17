# Databricks notebook source
import os, json, requests, config

def main():
    ok = True
    for p in [config.FAISS_PATH, config.META_PATH]:
        print("Check:", p, "->", "OK" if os.path.exists(p) else "MISSING")
        ok = ok and os.path.exists(p)

    try:
        r = requests.post(config.LM_STUDIO_URL, json={
            "model": config.LM_STUDIO_MODEL,
            "messages": [{"role":"system","content":"pong"}],
            "max_tokens": 5
        }, timeout=10)
        r.raise_for_status()
        print("LM Studio: OK")
    except Exception as e:
        ok = False
        print("LM Studio: ERROR ->", e)

    # Meta quick view
    if os.path.exists(config.META_PATH):
        meta = json.load(open(config.META_PATH, "r", encoding="utf-8"))
        print("Meta:", meta.get("meta", {}))

    return ok

if __name__ == "__main__":
    main()
