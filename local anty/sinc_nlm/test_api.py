import notebooklm_mcp.auth as nlm_auth
import requests
import json
import urllib.parse

tokens = nlm_auth.load_cached_tokens()
cookies = {}
if hasattr(tokens, "cookies") and isinstance(tokens.cookies, dict):
    cookies = tokens.cookies

s = requests.Session()
for k, v in cookies.items():
    s.cookies.set(k, v, domain=".google.com")

query = "'1NT-mLUDmbRoAlSIdvvynOhlvgD41jRM6' in parents"
q_encoded = urllib.parse.quote(query)
url = f"https://clients6.google.com/drive/v2internal/files?q={q_encoded}&fields=items(id,title,mimeType)&maxResults=10"

r = s.get(url, headers={"X-Drive-First-Party": "notebooklm"}, timeout=15)
print("Status:", r.status_code)
print("Response:", r.text[:500])
