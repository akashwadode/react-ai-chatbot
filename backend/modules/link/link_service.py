import hashlib
import hmac
import os
import time
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

SECRET = os.getenv("SIGNED_URL_SECRET")
BASE_URL = os.getenv("BASE_URL")

if not SECRET or not BASE_URL:
    raise ValueError("SIGNED_URL_SECRET and BASE_URL must be set in .env")


def hash_patient_id(patient_id: str) -> str:
    """
    Returns the SHA‑256 hash of the patient ID (as a string) in hex format.
    """
    return hashlib.sha256(patient_id.encode()).hexdigest()


def sign_payload(payload: str) -> str:
    return hmac.new(
        SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_signed_link(pid_hash: str, rid: str, expiry_minutes: int = 10) -> str:
    """
    Generates a signed URL for a report.
    - pid_hash: hashed patient ID (output of hash_patient_id)
    - rid: report ID (as string)
    - expiry_minutes: validity in minutes
    """
    exp = int(time.time() * 1000) + (expiry_minutes * 60 * 1000)   # milliseconds
    payload = f"{pid_hash}|{rid}|{exp}"
    sig = sign_payload(payload)

    params = {
        "pid": pid_hash,
        "rid": rid,
        "exp": exp,
        "sig": sig
    }
    return f"{BASE_URL}/report?{urlencode(params)}"


def validate_token(pid: str, rid: str, exp: str, sig: str) -> dict:
    from fastapi import HTTPException
    if not pid or not rid or not exp or not sig:
        raise HTTPException(status_code=401, detail="Missing access token")

    if int(exp) < time.time() * 1000:
        raise HTTPException(status_code=401, detail="Link expired")

    expected = sign_payload(f"{pid}|{rid}|{exp}")
    if expected != sig:
        raise HTTPException(status_code=401, detail="Invalid signature")

    return {"pid": pid, "rid": rid}