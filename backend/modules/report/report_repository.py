from core.database import get_connection

def get_patient_by_hash(pid_hash: str):
    print("=== DEBUG repository.py ===")
    print("Looking for pid_hash:", pid_hash)

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT patient_id, name, age, gender
        FROM dev.patients_details
        WHERE encode(digest(patient_id::text, 'sha256'), 'hex') = %s
    """
    print("Executing query:", query)
    print("With param:", pid_hash)

    cursor.execute(query, (pid_hash,))
    patient = cursor.fetchone()
    print("Patient fetched:", patient)

    cursor.close()
    conn.close()

    return patient


def get_patient_tests(patient_id: str):
    print("=== DEBUG get_patient_tests ===")
    print("Looking for tests for patient_id:", patient_id)

    conn = get_connection()
    cursor = conn.cursor()

    # Join through reports_upload_details to get all test results for this patient
    query = """
        SELECT pr.test_name, pr.result_value
        FROM dev.patient_result_details pr
        JOIN dev.reports_upload_details r ON pr.report_id = r.report_id
        WHERE r.patient_id = %s
    """
    print("Executing query:", query)
    print("With param:", patient_id)

    cursor.execute(query, (patient_id,))
    tests = cursor.fetchall()
    print("Tests fetched:", tests)

    cursor.close()
    conn.close()

    return tests