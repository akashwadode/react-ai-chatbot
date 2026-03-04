from core.database import get_connection
from modules.ai.llm import generate_response
from modules.report.service import load_patient_context
from shared.cache import (
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

# --- NEW: Buttons for direct parameter value answer ---
PARAMETER_VALUE_BUTTONS = [
    "Is {param} normal?",
    "What can improve {param}?",
    "Show important parameters",
    "Download Report",
]

def build_dynamic_buttons(intent: str, matched_param: str | None = None) -> list[str]:
    if intent == "greeting":
        return PROFILE_BUTTONS
    if intent == "profile":
        return ["How many tests", "How many parameters", "Hemoglobin", "Download Report"]
    if intent == "lab_parameter" and matched_param:
        # For AI‑explained parameter
        return [
            f"Is {matched_param} normal?",
            f"What can improve {matched_param}?",
            "Show important parameters",
            "Download Report",
        ]
    if intent == "lab_parameter_value" and matched_param:
        # For direct value answer – same buttons, different intent
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

        # ---------------- GET PATIENT ID ----------------
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
        cursor.close()
        conn.close()

        # --- NEW: Load (or create) patient context ONCE ---
        context = get_cached_context(patient_id)
        if not context:
            raw_context = load_patient_context(patient_id)
            set_cached_context(patient_id, raw_context)
            context = get_cached_context(patient_id)   # now includes 'text' and 'params'

        chat_memory = get_memory(patient_id)

        # ---------------- PARAMETER MATCH ----------------
        parameters = load_parameters_once()
        matched_param = next((p for p in parameters if p in question), None)

        # ---------------- LAB PARAMETER (NEW CACHED VERSION) ----------------
        if matched_param:
            # Try to get value from cached params dictionary
            value = context["params"].get(matched_param)

            if value is not None:
                # Direct answer from cache – no DB, no LLM
                return {
                    "answer": f"Your {matched_param} is {value}.",
                    "buttons": build_dynamic_buttons("lab_parameter_value", matched_param),
                    "intent": "lab_parameter_value"
                }
            else:
                # Parameter not found in patient's report
                return {
                    "answer": f"{matched_param} not found in your report.",
                    "buttons": build_dynamic_buttons("general"),
                    "intent": "general",
                }

        # ---------------- GENERAL QUESTION ----------------
        # (No matched parameter)
        final_prompt = f"""
            Answer the following question based on the patient report.

            Question: {question_raw}

            Patient Report:
            {context['text']}
            """

        ai_reply = generate_response(final_prompt, chat_memory)

        return {
            "answer": ai_reply,
            "buttons": build_dynamic_buttons("general"),
            "intent": "general",
        }

    except Exception as e:
        print("ERROR:", e)
        return {
            "answer": "Something went wrong while processing your request.",
            "buttons": DEFAULT_BUTTONS,
            "intent": "error",
        }