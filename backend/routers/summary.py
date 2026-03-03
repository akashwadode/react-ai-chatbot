from fastapi import APIRouter, Depends
from backend.middleware.token_validator import validate_signed_request
from backend.services.db_service import get_connection


router = APIRouter()

@router.get("/api/summary")
def get_summary(context=Depends(validate_signed_request)):

    pid = context["pid"]
    print("HASH PID FROM TOKEN:", pid)
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 👤 Patient Info
        cursor.execute("""
            SELECT PatientID, Name, Age, Gender
            FROM patient
            WHERE encode(digest(patientid::text, 'sha256'), 'hex') = %s
        """, (pid,))

        patient = cursor.fetchone()
        print("PATIENT FETCHED:", patient)

        if not patient:
            return {"error": "Patient not found"}

        patient_id = patient[0]

        # 🔍 Abnormal Check
        cursor.execute("""
        SELECT patientid, name, age, gender
        FROM patient
        WHERE encode(digest(patientid::text, 'sha256'), 'hex') = %s
        """, (pid,))


        abnormal = cursor.fetchone()

        status = "Attention Required" if abnormal else "Ready"

        cursor.close()
        conn.close()

        return {
            "patientName": patient[1],
            "age": patient[2],
            "gender": patient[3],
            "reportId": f"RPT-{patient_id}",
            "labRef": f"DL-{patient_id}",
            "status": status,
        }

    except Exception as e:
        return {"error": str(e)}
