from fastapi import APIRouter, HTTPException
from modules.whatsapp.whatsapp_service import (
    send_whatsapp_template,
    send_whatsapp_static_template,
    update_notification_status
)
from modules.whatsapp.whatsapp_repository import (
    fetch_pending_notification,
    increment_retry_or_fail,
    update_notification_status
)
from modules.link.link_service import hash_patient_id, generate_signed_link
from core.database import get_connection

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/send-report/{patient_id}")
async def send_report_via_whatsapp(patient_id: str):   # changed to str for UUID
    # ... same as before, but adjust for UUID (patient_id is now string)
    TEST_PHONE_NUMBER = "919876543210"
    pid_hash = hash_patient_id(patient_id)
    # Assuming report_id is 1 for testing – you may need to fetch the actual report ID
    signed_url = generate_signed_link(pid_hash, rid="1", expiry_minutes=1440)
    result = send_whatsapp_template(TEST_PHONE_NUMBER, "Test Patient", signed_url)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"message": "WhatsApp message sent", "response": result}


@router.post("/process-pending")
async def process_pending_notification():
    """
    Fetch one pending notification, send WhatsApp, update status.
    """
    # 1. Get a pending notification
    pending = fetch_pending_notification()
    if not pending:
        return {"message": "No pending notifications"}

    notification_id = pending["notification_id"]
    report_id = pending["report_id"]
    patient_whatsapp = pending["patient_whatsapp"]
    patient_name = pending["patient_name"]
    patient_id = pending["patient_id"]

    # 2. Validate phone number
    if not patient_whatsapp:
        # Mark as failed permanently (no phone number)
        update_notification_status(notification_id, status_id=2, retry_count=1)
        raise HTTPException(status_code=400, detail="Patient has no phone number")

    # 3. Generate signed URL (expiry 1 day = 1440 minutes)
    pid_hash = hash_patient_id(str(patient_id))
    signed_url = generate_signed_link(pid_hash, rid=str(report_id), expiry_minutes=1440)

    # 4. Send WhatsApp
    result = send_whatsapp_template(patient_whatsapp, patient_name, signed_url)

    # 5. Update notification record based on result
    conn = get_connection()
    cursor = conn.cursor()
    if "error" in result:
        # Increment retry count
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET retry_count = retry_count + 1,
                processed_at = NOW()
            WHERE notification_id = %s
            RETURNING retry_count
        """, (notification_id,))
        retry_count = cursor.fetchone()[0]
        if retry_count >= 3:
            cursor.execute("""
                UPDATE dev.patient_notification_details
                SET notification_status_id = 2
                WHERE notification_id = %s
            """, (notification_id,))
        conn.commit()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=result["error"])
    else:
        # Success
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET notification_status_id = 1,
                processed_at = NOW(),
                retry_count = 0
            WHERE notification_id = %s
        """, (notification_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Notification sent", "response": result}

@router.post("/process-pending-static")
async def process_pending_notification_static():
    """
    Process one pending notification using the static template (no dynamic URL).
    """
    pending = fetch_pending_notification()
    if not pending:
        return {"message": "No pending notifications"}

    notification_id = pending["notification_id"]
    patient_whatsapp = pending["patient_whatsapp"]
    patient_name = pending["patient_name"]

    if not patient_whatsapp:
        update_notification_status(notification_id, status_id=2, retry_count=1)
        raise HTTPException(status_code=400, detail="Patient has no phone number")

    # Send using static template (no URL needed)
    result = send_whatsapp_static_template(patient_whatsapp, patient_name)

    if "error" in result:
        # Increment retry count, mark as failed after 3 attempts
        increment_retry_or_fail(notification_id)
        raise HTTPException(status_code=500, detail=result["error"])
    else:
        update_notification_status(notification_id, status_id=1, retry_count=0)
        return {"message": "Notification sent (static)", "response": result}