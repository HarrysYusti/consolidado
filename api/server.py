from fastapi import FastAPI, Depends, Request, Response, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.router import Router
from security.auth import require_api_key
from core.session import get_or_create_session_id
import json, config, os

app = FastAPI(title="DIANA API")
router = Router()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskIn(BaseModel):
    question: str
    session_id: str | None = None  


@app.on_event("startup")
def _startup_checks():
    if not os.path.exists(config.FAISS_PATH) or not os.path.exists(config.META_PATH):
        raise RuntimeError("Faltan artefactos persistentes (faiss.index o meta.json).")
    with open(config.META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("meta", {}).get("embed_model") and meta["meta"]["embed_model"] != config.EMBED_MODEL:
        raise RuntimeError("El índice fue construido con otro modelo de embeddings.")

@app.get("/health")
def health():
    try:
        with open(config.META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        return {
            "ok": True,
            "total_items": meta.get("meta", {}).get("total_items"),
            "vector_dim": meta.get("meta", {}).get("vector_dim"),
            "embed_model": meta.get("meta", {}).get("embed_model"),
            "index_readonly": config.INDEX_READONLY
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
@app.post("/ask")
def ask(in_data: AskIn, request: Request, response: Response, _auth=Depends(require_api_key)):
    try:
        sid = in_data.session_id or get_or_create_session_id(request, response)
        result = router.route(in_data.question, sid=sid)
        result["session_id"] = sid
        return result
    except Exception as e:
        logging.getLogger("diana").error("ASK error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=502, detail=f"Upstream error: {type(e).__name__}: {e}")

@app.post("/ask/clear")
def ask_clear(in_data: AskIn, request: Request, response: Response, _auth=Depends(require_api_key)):
    from memory.store import STORE
    sid = in_data.session_id or get_or_create_session_id(request, response)
    STORE.clear(sid)
    return {"ok": True, "session_id": sid, "message": "Conversación borrada"}
