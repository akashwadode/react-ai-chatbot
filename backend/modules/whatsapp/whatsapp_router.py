from fastapi import APIRouter, HTTPException
from modules.whatsapp.whatsapp_service import (
    send_whatsapp_template,
    send_whatsapp_new_template,
)
from modules.whatsapp.whatsapp_repository import (
    fetch_pending_notification,
    fetch_all_pending_notifications,
    increment_retry_or_fail,
    update_notification_status,
)
from modules.link.link_service import hash_patient_id, generate_signed_link

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.post("/send-report/{patient_id}")
async def send_report_via_whatsapp(patient_id: str):
    """
    Manual test endpoint – sends to a hardcoded number using the default template.
    """
    TEST_PHONE_NUMBER = "919876543210"
    pid_hash = hash_patient_id(patient_id)
    # Assuming report_id is 1 for testing – adjust as needed
    signed_url = generate_signed_link(pid_hash, rid="1", expiry_minutes=1440)
    result = send_whatsapp_template(TEST_PHONE_NUMBER, "Test Patient", signed_url)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return {"message": "WhatsApp message sent", "response": result}


@router.post("/process-pending")
async def process_pending_notification():
    """
    Process one pending notification using the default template (with button).
    """
    pending = fetch_pending_notification()
    if not pending:
        return {"message": "No pending notifications"}

    notification_id = pending["notification_id"]
    report_id = pending["report_id"]
    patient_whatsapp = pending["patient_whatsapp"]
    patient_name = pending["patient_name"]
    patient_id = pending["patient_id"]

    if not patient_whatsapp:
        update_notification_status(notification_id, status_id=2, retry_count=1)
        raise HTTPException(status_code=400, detail="Patient has no phone number")

    pid_hash = hash_patient_id(str(patient_id))
    signed_url = generate_signed_link(pid_hash, rid=str(report_id), expiry_minutes=1440)

    result = send_whatsapp_template(patient_whatsapp, patient_name, signed_url)

    if "error" in result:
        increment_retry_or_fail(notification_id)
        raise HTTPException(status_code=500, detail=result["error"])
    else:
        update_notification_status(notification_id, status_id=1, retry_count=0)
        return {"message": "Notification sent", "response": result}

# for one notification at a time 
# @router.post("/process-pending-new")
# async def process_pending_notification_new():
#     """
#     Process one pending notification using the new template 'report_ready_notification_2'.
#     Requires lab_name from database.
#     """
#     pending = fetch_pending_notification()
#     if not pending:
#         return {"message": "No pending notifications"}

#     notification_id = pending["notification_id"]
#     patient_whatsapp = pending["patient_whatsapp"]
#     patient_name = pending["patient_name"]
#     lab_name = pending["lab_name"]
#     report_id = pending["report_id"]
#     patient_id = pending["patient_id"]

#     if not patient_whatsapp:
#         update_notification_status(notification_id, status_id=2, retry_count=1)
#         raise HTTPException(status_code=400, detail="Patient has no phone number")

#     pid_hash = hash_patient_id(str(patient_id))
#     signed_url = generate_signed_link(pid_hash, rid=str(report_id), expiry_minutes=1440)

#     result = send_whatsapp_new_template(patient_whatsapp, patient_name, lab_name, signed_url)

#     if "error" in result:
#         increment_retry_or_fail(notification_id)
#         raise HTTPException(status_code=500, detail=result["error"])
#     else:
#         update_notification_status(notification_id, status_id=1, retry_count=0)
#         return {"message": "Notification sent (new template)", "response": result}
    
@router.post("/process-pending-new")
async def process_pending_notification_new():
    """
    Process ALL pending notifications using the new template 'report_ready_notification_2'.
    Returns summary of successful and failed attempts.
    """
    pending_list = fetch_all_pending_notifications()
    if not pending_list:
        return {"message": "No pending notifications"}

    results = {
        "total": len(pending_list),
        "success": 0,
        "failed": 0,
        "details": []
    }

    for pending in pending_list:
        notification_id = pending["notification_id"]
        patient_whatsapp = pending["patient_whatsapp"]
        patient_name = pending["patient_name"]
        lab_name = pending["lab_name"]
        report_id = pending["report_id"]
        patient_id = pending["patient_id"]

        # Skip if no phone number
        if not patient_whatsapp:
            update_notification_status(notification_id, status_id=2, retry_count=1)
            results["failed"] += 1
            results["details"].append({
                "notification_id": notification_id,
                "status": "failed",
                "reason": "No phone number"
            })
            continue

        # Generate signed URL
        pid_hash = hash_patient_id(str(patient_id))
        signed_url = generate_signed_link(pid_hash, rid=str(report_id), expiry_minutes=1440)

        # Send WhatsApp
        result = send_whatsapp_new_template(patient_whatsapp, patient_name, lab_name, signed_url)

        if "error" in result:
            increment_retry_or_fail(notification_id)
            results["failed"] += 1
            results["details"].append({
                "notification_id": notification_id,
                "status": "failed",
                "reason": result["error"]
            })
        else:
            update_notification_status(notification_id, status_id=1, retry_count=0)
            results["success"] += 1
            results["details"].append({
                "notification_id": notification_id,
                "status": "success"
            })

    return results