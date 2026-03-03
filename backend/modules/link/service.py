import hashlib
import hmac
import os
import time
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")

SECRET = os.getenv("SIGNED_URL_SECRET")
BASE_URL = os.getenv("BASE_URL")


# 🔐 Hash Patient ID
def hash_patient_id(pid: int):
    return hashlib.sha256(str(pid).encode()).hexdigest()


# 🔐 Sign payload
def sign_payload(payload: str):
    return hmac.new(
        SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


# 🔐 Generate Signed Link
def generate_signed_link(pid, rid, minutes=10):
    exp = int(time.time() * 1000) + (minutes * 60 * 1000)
    payload = f"{pid}|{rid}|{exp}"
    sig = sign_payload(payload)

    return f"{BASE_URL}/report?pid={pid}&rid={rid}&exp={exp}&sig={sig}"


# 🔐 Validate Token
def validate_token(pid, rid, exp, sig):

    if not pid or not rid or not exp or not sig:
        raise HTTPException(status_code=401, detail="Missing access token")

    expected = sign_payload(f"{pid}|{rid}|{exp}")

    if expected != sig:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"pid": pid, "rid": rid}