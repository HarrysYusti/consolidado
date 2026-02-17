# Databricks notebook source
# core/session.py
import uuid
from fastapi import Request, Response

HEADER_SID = "X-Session-Id"
COOKIE_SID = "DIANA_SID"

def get_or_create_session_id(request: Request, response: Response) -> str:
    sid = (
        request.headers.get(HEADER_SID)
        or request.query_params.get("session_id")
        or request.cookies.get(COOKIE_SID)
    )
    if not sid:
        sid = uuid.uuid4().hex
        # en HTTPS usa secure=True
        response.set_cookie(
            COOKIE_SID, sid, httponly=False, samesite="Lax", path="/"
        )
    return sid
