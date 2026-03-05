"""
modules/whatsapp/whatsapp_router.py

Defines FastAPI endpoints for sending WhatsApp messages.
Currently provides a test endpoint that sends a report link to a hardcoded number.
"""

from fastapi import APIRouter, HTTPException
from modules.whatsapp.whatsapp_service import send_whatsapp_template
from modules.link.link_service import hash_patient_id, generate_signed_link

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/send-report/{patient_id}")
async def send_report_via_whatsapp(patient_id: int):
    """
    Endpoint to send a WhatsApp message with a signed report link.
    For testing, it sends to a hardcoded number (your own).
    Later you can fetch the patient's actual phone number from the database.
    """
    # TODO: Replace with actual phone number from DB
    TEST_PHONE_NUMBER = "919876543210"   # your number, without '+'

    # Compute the hashed patient ID
    pid_hash = hash_patient_id(patient_id)

    # Generate the signed URL for the patient's report (expiry, say, 1 day = 1440 minutes)
    signed_url = generate_signed_link(pid_hash, report_id=1, expiry_minutes=1440)

    # Call the service to send the message
    result = send_whatsapp_template(TEST_PHONE_NUMBER, signed_url)

    # If the service returned an error, raise an HTTP exception
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    # Otherwise return success
    return {"message": "WhatsApp message sent", "response": result}