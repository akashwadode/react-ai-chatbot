import hashlib
import hmac
import os
import time
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# Load from environment (use the same secret for both generation and validation)
SECRET = os.getenv("SIGNED_URL_SECRET")      # e.g., "mysectretkey"
BASE_URL = os.getenv("BASE_URL")              # e.g., "https://yourdomain.com"

if not SECRET or not BASE_URL:
    raise ValueError("SIGNED_URL_SECRET and BASE_URL must be set in .env")


def hash_patient_id(pid: int) -> str:
    """
    Returns the SHA‑256 hash of the patient ID as a hex string.
    This hash is used as the 'pid' parameter in the signed URL.
    """
    return hashlib.sha256(str(pid).encode()).hexdigest()


def sign_payload(payload: str) -> str:
    """
    Creates an HMAC‑SHA256 signature for the given payload using the secret.
    """
    return hmac.new(
        SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_signed_link(pid_hash: str, rid: int, expiry_minutes: int = 10) -> str:
    """
    Generates a signed URL for accessing a report.

    Args:
        pid_hash: The hashed patient ID (output of hash_patient_id).
        rid: Report ID.
        expiry_minutes: Link validity duration in minutes (default 10).

    Returns:
        Full signed URL string.
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
    """
    Validates the signature and expiry of a request.
    Raises HTTPException if invalid – intended for use in FastAPI dependency.
    """
    from fastapi import HTTPException

    if not pid or not rid or not exp or not sig:
        raise HTTPException(status_code=401, detail="Missing access token")

    # Check expiry (exp is in milliseconds)
    if int(exp) < time.time() * 1000:
        raise HTTPException(status_code=401, detail="Link expired")

    expected_sig = sign_payload(f"{pid}|{rid}|{exp}")
    if expected_sig != sig:
        raise HTTPException(status_code=401, detail="Invalid signature")

    return {"pid": pid, "rid": rid}