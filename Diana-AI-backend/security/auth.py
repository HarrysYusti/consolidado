# Databricks notebook source
# security/auth.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
import config

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer = HTTPBearer(auto_error=False)

def require_api_key(
    api_key: str | None = Depends(api_key_header),
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
):
    if not config.REQUIRE_AUTH:
        return
    token = api_key or (cred.credentials if cred else None)
    if not token or token not in config.API_TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
