from fastapi import APIRouter, Depends
from backend.modules.link.router import validate_signed_request
from backend.modules.report.service import build_summary

router = APIRouter()


@router.get("/api/summary")
def get_summary(context=Depends(validate_signed_request)):
    pid_hash = context["pid"]
    return build_summary(pid_hash)