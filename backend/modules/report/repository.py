from backend.core.database import get_connection


def get_patient_by_hash(pid_hash: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT PatientID, Name, Age, Gender
        FROM Patient
        WHERE encode(digest(PatientID::text, 'sha256'), 'hex') = %s
    """, (pid_hash,))

    patient = cursor.fetchone()
    cursor.close()
    conn.close()

    return patient


def get_patient_tests(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tp.ParameterName, tr.ResultValue
        FROM TestResult tr
        JOIN TestParameter tp
        ON tr.TestParameterId = tp.TestParameterId
        WHERE tr.PatientID = %s
    """, (patient_id,))

    tests = cursor.fetchall()
    cursor.close()
    conn.close()

    return tests