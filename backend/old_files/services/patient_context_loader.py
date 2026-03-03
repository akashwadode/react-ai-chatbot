from backend.services.db_service import get_connection

def load_patient_context(patient_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Name, Age, Gender
        FROM Patient
        WHERE PatientID = %s
    """, (patient_id,))

    patient = cursor.fetchone()

    if not patient:
        return ""

    name, age, gender = patient

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

    report_summary = ""

    for param, value in tests:
        if value:
            report_summary += f"{param}: {value}\n"

    context = f"""
Patient Information:
Name: {name}
Age: {age}
Gender: {gender}

Test Results:
{report_summary}
"""

    return context
