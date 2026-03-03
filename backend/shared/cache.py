"""
shared/cache.py

This file handles all in-memory caching used in the application.

We store:
1. PARAMETERS_CACHE → List of all lab parameters (loaded once from DB)
2. PATIENT_CONTEXT_CACHE → Stores generated report context per patient
3. PATIENT_MEMORY_CACHE → Stores chat history per patient (for AI memory)

⚠️ Note:
This is simple in-memory caching.
Data will reset when server restarts.
Suitable for small-scale / single-instance deployments.
"""

from backend.core.database import get_connection

# -------------------------------
# 🔬 Parameter Cache
# -------------------------------

_PARAMETERS_CACHE = []


def load_parameters_once():
    """
    Loads all test parameter names from DB only once.
    Used for detecting lab parameter keywords in chat.
    """
    global _PARAMETERS_CACHE

    if _PARAMETERS_CACHE:
        return _PARAMETERS_CACHE

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT LOWER(ParameterName)
        FROM TestParameter
    """)

    rows = cursor.fetchall()
    _PARAMETERS_CACHE = [r[0] for r in rows]

    cursor.close()
    conn.close()

    print("✅ PARAMETERS LOADED INTO CACHE")

    return _PARAMETERS_CACHE


# -------------------------------
# 📄 Patient Report Context Cache
# -------------------------------

# In shared/cache.py

_PATIENT_CONTEXT_CACHE = {}   # now will hold dicts with keys 'text' and 'params'

def get_cached_context(patient_id):
    """Returns cached context dict for a patient (or None)."""
    return _PATIENT_CONTEXT_CACHE.get(patient_id)

def set_cached_context(patient_id, context_text):
    """
    Stores report context and also parses it into a parameter dict.
    context_text is a multiline string like "hemoglobin: 13.2\nglucose: 95"
    """
    params_dict = {}
    for line in context_text.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            params_dict[key.strip().lower()] = val.strip()

    _PATIENT_CONTEXT_CACHE[patient_id] = {
        "text": context_text,
        "params": params_dict
    }
# -------------------------------
# 🧠 Chat Memory Cache
# -------------------------------

_PATIENT_MEMORY_CACHE = {}


def get_memory(patient_id):
    """
    Returns chat history list for a patient.
    If not exists, initializes empty list.
    """
    return _PATIENT_MEMORY_CACHE.setdefault(patient_id, [])