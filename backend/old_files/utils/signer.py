import hashlib
import hmac
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")


SECRET = os.getenv("SIGNED_URL_SECRET")

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

    import time

    exp = int(time.time() * 1000) + (minutes * 60 * 1000)
    payload = f"{pid}|{rid}|{exp}"
    sig = sign_payload(payload)

    BASE_URL = os.getenv("BASE_URL")

    return f"{BASE_URL}/report?pid={pid}&rid={rid}&exp={exp}&sig={sig}"
