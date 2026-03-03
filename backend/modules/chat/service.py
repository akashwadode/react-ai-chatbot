from backend.services.db_service import get_connection
from backend.modules.ai.llm import generate_response
from backend.services.patient_context_loader import load_patient_context
from backend.shared.cache import (
    load_parameters_once,
    get_cached_context,
    set_cached_context,
    get_memory,
)

DEFAULT_BUTTONS = [
    "Hemoglobin",
    "How many parameters",
    "How many tests",
    "Download Report",
]

PROFILE_BUTTONS = [
    "What is my name",
    "What is my age",
    "What is my gender",
    "How many tests",
]

REPORT_INSIGHT_BUTTONS = [
    "Explain abnormal values",
    "Show important parameters",
    "How many parameters",
    "Download Report",
]


def build_dynamic_buttons(intent: str, matched_param: str | None = None) -> list[str]:
    if intent == "greeting":
        return PROFILE_BUTTONS

    if intent == "profile":
        return ["How many tests", "How many parameters", "Hemoglobin", "Download Report"]

    if intent == "lab_parameter" and matched_param:
        return [
            f"Is {matched_param} normal?",
            f"What can improve {matched_param}?",
            "Show important parameters",
            "Download Report",
        ]

    if intent == "general":
        return REPORT_INSIGHT_BUTTONS

    return DEFAULT_BUTTONS


def handle_chat(pid_hash: str, question_raw: str):

    question = question_raw.strip().lower()

    GREETING_WORDS = ["hi", "hello", "hey"]

    PREDEFINED_QUERIES = {
        "what is my name": "Name",
        "my name": "Name",
        "who am i": "Name",
        "what is my age": "Age",
        "my age": "Age",
        "what is my gender": "Gender",
        "my gender": "Gender",
    }

    try:

        # ---------------- GREETING ----------------
        if question in GREETING_WORDS:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT Name
                FROM Patient
                WHERE encode(digest(PatientID::text, 'sha256'), 'hex') = %s
                """,
                (pid_hash,),
            )

            patient = cursor.fetchone()
            cursor.close()
            conn.close()

            if patient:
                return {
                    "answer": f"Hi {patient[0]}! How can I help you with your report today?",
                    "buttons": build_dynamic_buttons("greeting"),
                    "intent": "greeting",
                }

            return {
                "answer": "Hello! How can I help you today?",
                "buttons": build_dynamic_buttons("greeting"),
                "intent": "greeting",
            }

        # ---------------- PROFILE ----------------
        for key, column in PREDEFINED_QUERIES.items():
            if key in question:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    f"""
                    SELECT {column}
                    FROM Patient
                    WHERE encode(digest(PatientID::text, 'sha256'), 'hex') = %s
                    """,
                    (pid_hash,),
                )

                result = cursor.fetchone()
                cursor.close()
                conn.close()

                if result:
                    return {
                        "answer": f"Your {column.lower()} is {result[0]}.",
                        "buttons": build_dynamic_buttons("profile"),
                        "intent": "profile",
                    }

        # ---------------- PARAMETER MATCH ----------------
        parameters = load_parameters_once()
        matched_param = next((p for p in parameters if p in question), None)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT PatientID
            FROM Patient
            WHERE encode(digest(PatientID::text, 'sha256'), 'hex') = %s
            """,
            (pid_hash,),
        )

        patient = cursor.fetchone()

        if not patient:
            cursor.close()
            conn.close()
            return {
                "answer": "Patient not found",
                "buttons": DEFAULT_BUTTONS,
                "intent": "error",
            }

        patient_id = patient[0]
        chat_memory = get_memory(patient_id)

        # ---------------- GENERAL QUESTION ----------------
        if not matched_param:
            cursor.close()
            conn.close()

            context_data = get_cached_context(patient_id)

            if not context_data:
                context_data = load_patient_context(patient_id)
                set_cached_context(patient_id, context_data)

            final_prompt = f"""
Answer the following question based on the patient report.

Question: {question_raw}

Patient Report:
{context_data}
"""

            ai_reply = generate_response(final_prompt, chat_memory)

            return {
                "answer": ai_reply,
                "buttons": build_dynamic_buttons("general"),
                "intent": "general",
            }

        # ---------------- LAB PARAMETER ----------------
        cursor.execute(
            """
            SELECT tp.TestParameterId, tp.ParameterName
            FROM TestParameter tp
            JOIN TestResult tr
            ON tp.TestParameterId = tr.TestParameterId
            WHERE tr.PatientID = %s
            AND LOWER(tp.ParameterName) = LOWER(%s)
            LIMIT 1
            """,
            (patient_id, matched_param),
        )

        param = cursor.fetchone()

        if not param:
            cursor.close()
            conn.close()
            return {
                "answer": f"{matched_param} not found in your report",
                "buttons": build_dynamic_buttons("general"),
                "intent": "general",
            }

        param_id = param[0]
        parameter_name = param[1]

        cursor.execute(
            """
            SELECT ResultValue
            FROM TestResult
            WHERE PatientID = %s
            AND TestParameterId = %s
            """,
            (patient_id, param_id),
        )

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result or result[0] is None:
            return {
                "answer": f"{parameter_name} test is available but no result value is recorded in your report.",
                "buttons": build_dynamic_buttons("lab_parameter", parameter_name),
                "intent": "lab_parameter",
            }

        lab_value = result[0]

        prompt = f"""
Patient's {parameter_name} test result is {lab_value}.

Explain in 2-3 short simple lines:
- Is this normal or abnormal?
- What does it mean for health?
"""

        ai_explanation = generate_response(prompt, chat_memory)

        return {
            "answer": ai_explanation,
            "buttons": build_dynamic_buttons("lab_parameter", parameter_name),
            "intent": "lab_parameter",
        }

    except Exception as e:
        print("ERROR:", e)
        return {
            "answer": "Something went wrong while processing your request.",
            "buttons": DEFAULT_BUTTONS,
            "intent": "error",
        }