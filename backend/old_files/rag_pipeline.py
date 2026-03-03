import ollama
from backend.services.db_service import get_connection

# 🟢 Fetch patient data once from DB
def fetch_patient_context(patient_id):

    conn = get_connection()
    cursor = conn.cursor()

    # 👤 Personal Info
    cursor.execute("""
        SELECT name, age, gender
        FROM patient
        WHERE patientid=%s
    """, (patient_id,))

    patient = cursor.fetchone()

    # 🧪 Lab Results
    cursor.execute("""
        SELECT tp.ParameterName, tr.ResultValue
        FROM testresult tr
        JOIN testparameter tp
        ON tp.TestParameterId = tr.TestParameterId
        WHERE tr.PatientID=%s
    """, (patient_id,))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert lab results to readable format
    test_text = ""
    for t in tests:
        test_text += f"{t[0]}: {t[1]}\n"

    context = f"""
Patient Name: {patient[0]}
Age: {patient[1]}
Gender: {patient[2]}

Lab Test Results:
{test_text}
"""

    return context


# 🧠 Main RAG function
def run_rag(question, patient_id):

    context = fetch_patient_context(patient_id)

    prompt = f"""
You are a medical report assistant.

Use ONLY the following patient report data to answer.

{context}

Question:
{question}

Answer clearly based only on this report.
"""

    response = ollama.chat(
        model='llama3',
        messages=[
            {"role":"user","content":prompt}
        ]
    )

    return {
        "answer": response['message']['content']
    }
