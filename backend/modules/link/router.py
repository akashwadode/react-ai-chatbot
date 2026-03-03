from fastapi import APIRouter, Request, Depends
from backend.modules.link.service import (
    hash_patient_id,
    generate_signed_link,
    validate_token
)

router = APIRouter()


@router.get("/create-link")
def create_link(patientId: int):
    pid = hash_patient_id(patientId)
    link = generate_signed_link(pid, 1, 10)
    return {"reportLink": link}


async def validate_signed_request(request: Request):
    pid = request.query_params.get("pid")
    rid = request.query_params.get("rid")
    exp = request.query_params.get("exp")
    sig = request.query_params.get("sig")

    return validate_token(pid, rid, exp, sig)