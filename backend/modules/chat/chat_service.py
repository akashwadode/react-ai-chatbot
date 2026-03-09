from core.database import get_connection
from modules.ai.llm import generate_response
from modules.report.report_service import load_patient_context
from modules.ai.prompts import build_user_prompt
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

# Buttons for direct parameter value answer
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
        return [
            f"Is {matched_param} normal?",
            f"What can improve {matched_param}?",
            "Show important parameters",
            "Download Report",
        ]
    if intent == "lab_parameter_value" and matched_param:
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
        "what is my name": "name",
        "my name": "name",
        "who am i": "name",
        "what is my age": "age",
        "my age": "age",
        "what is my gender": "gender",
        "my gender": "gender",
    }

    try:
        # ---------------- GREETING ----------------
        if question in GREETING_WORDS:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name
                FROM dev.patients_details
                WHERE encode(digest(patient_id::text, 'sha256'), 'hex') = %s
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
                    FROM dev.patients_details
                    WHERE encode(digest(patient_id::text, 'sha256'), 'hex') = %s
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
            SELECT patient_id
            FROM dev.patients_details
            WHERE encode(digest(patient_id::text, 'sha256'), 'hex') = %s
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

        # --- Load (or create) patient context ONCE ---
        context = get_cached_context(patient_id)
        if not context:
            raw_context = load_patient_context(patient_id)
            set_cached_context(patient_id, raw_context)
            context = get_cached_context(patient_id)   # now includes 'text' and 'params'

        chat_memory = get_memory(patient_id)

               # ---------------- PARAMETER MATCH ----------------
        parameters = load_parameters_once()
        matched_param = next((p for p in parameters if p in question), None)

        # ---------------- ENHANCED INTENT DETECTION ----------------
        if matched_param:
            # Define keyword sets
            meaning_keywords = ["explain", "define", "meaning", "tell me about"]
            interpretation_keywords = ["normal", "abnormal", "high", "low"]   # <-- new
            ambiguous_phrases = ["what is"]

            # Check for strong meaning or interpretation indicators
            if any(kw in question for kw in meaning_keywords + interpretation_keywords):
                # Explanatory question → send to LLM
                pass  # fall through to general question handling

            # Check ambiguous phrases like "what is"
            elif any(ap in question for ap in ambiguous_phrases):
                if "my" in question:
                    # "what is my X" → value request
                    value = context["params"].get(matched_param)
                    if value is not None:
                        return {
                            "answer": f"Your {matched_param} is {value}.",
                            "buttons": build_dynamic_buttons("lab_parameter_value", matched_param),
                            "intent": "lab_parameter_value"
                        }
                    else:
                        return {
                            "answer": f"{matched_param} not found in your report.",
                            "buttons": build_dynamic_buttons("general"),
                            "intent": "general",
                        }
                else:
                    # "what is X" without "my" → explanatory
                    pass  # fall through to LLM

            else:
                # No special keywords → assume value request
                value = context["params"].get(matched_param)
                if value is not None:
                    return {
                        "answer": f"Your {matched_param} is {value}.",
                        "buttons": build_dynamic_buttons("lab_parameter_value", matched_param),
                        "intent": "lab_parameter_value"
                    }
                else:
                    return {
                        "answer": f"{matched_param} not found in your report.",
                        "buttons": build_dynamic_buttons("general"),
                        "intent": "general",
                    }
        # ---------------- GENERAL QUESTION ----------------
        # (No parameter matched, or matched but identified as explanatory)
        final_prompt = build_user_prompt(question_raw, context['text'])
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