from fastapi import APIRouter
from backend.utils.signer import hash_patient_id, generate_signed_link

print("📦 LINK ROUTER FILE LOADED")

router = APIRouter()

@router.get("/create-link")
def create_link(patientId: int):
    print("🔥 CREATE LINK HIT")
    pid = hash_patient_id(patientId)
    link = generate_signed_link(pid, 1, 10)
    return {"reportLink": link}
