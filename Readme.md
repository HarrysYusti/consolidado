# Sync Base de datos Vectorial

- Build (una sola vez, para generar la base de datos vectorial):
- Coloca data.xlsx en data/.
- Ejecuta scripts/ingest_data.py para generar corpus.jsonl.
- Ejecuta ingest_embeddings.py (o tu paso de embeddings) para crear faiss.index y actualizar meta.json con embed_model y vector_dim.

# Run (servidor):

- El servidor no reconstruye índice ni embeddings del corpus.
- Requiere FAISS_PATH y META_PATH existentes.
- Solo embebe queries en tiempo de ejecución.

# Checklist de ajustes

-  .env.example → nuevas claves y rutas a artefactos.
- config.py → leer flags/paths; no hay lógica de construcción.
- scripts/ingest_data.py → asegura embed_model y vector_dim en meta.json (o usa ingest_embeddings.py).
- tools/embeddings.py → solo para queries, lazy load.
- rag/retriever.py → carga faiss.index/meta.json, maybe_reload() opcional.
- rag/pipeline.py → usa Retriever persistente; no reindexa.
- agents/chat_agent.py → igual; top-k por config.
- api/server.py → startup checks + /health; no reingesta.
- scripts/healthcheck.py → valida artefactos y LM Studio.


# Mejoras de desempeño recomendadas

- Conexión al LLM
- Usa httpx.AsyncClient con pool y keep-alive (si pasas a async).
- Tiempo de espera: timeout=(5, 60) (connect, read).
- Streaming opcional para UI.
- Embeddings
- Cache de embeddings de preguntas frecuentes (dict LRU por texto normalizado).

# FAISS

- Si el corpus crece: IndexIVFFlat + entrenar, o HNSW (faiss-hnsw) para ANN.
- Cuantización PQ u OPQ si pesa mucho.
- Carga en caliente y opción INDEX_AUTORELOAD_SEC para rotar índice sin reiniciar.

# JSON

- Cambia a orjson en FastAPI (ORJSONResponse) para respuestas más rápidas.
- Uvicorn/Gunicorn
- Producción: --workers N (N ≈ cores), --loop uvloop, --http httptools.

# Límites

- Usa MAX_CTX_CHARS para evitar prompts gigantes.
- Poner un límite de longitud en question (p. ej., 1000 chars).
- Reintentos con backoff al LLM sólo 1 vez.

# Observabilidad

- Log de latencias de: FAISS, LLM, total.
- Métricas Prometheus (opcional) y request IDs.
- Rate limit y cuota
- slowapi o starlette-limiter para evitar abuso por token.
- Telemetría por token para facturación interna.

# Versiones de DIANA

- Mayor (v2.0.0) → cambios incompatibles.
- Menor (v1.1.0) → nuevas funciones compatibles.
- Patch (v1.1.1) → correcciones sin cambios funcionales grandes.

# Comandos Típicos

1) Crear venv e instalar dependencias
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt

2) Configurar .env desde el template
cp .env.example .env
# (si cambias modelo/puerto en LM Studio, ajusta aquí)

3) Ingesta inicial (leer Excel y construir índice)
python scripts/ingest_data.py

4) Levantar API (Fase 1)
uvicorn api.server:app --reload --port 8000

5) Probar
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" \
  -d '{"question":"¿Qué es Receta Bruta?"}'
