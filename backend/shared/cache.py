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

_PATIENT_CONTEXT_CACHE = {}


def get_cached_context(patient_id):
    """
    Returns cached report context for a patient (if exists).
    """
    return _PATIENT_CONTEXT_CACHE.get(patient_id)


def set_cached_context(patient_id, context):
    """
    Stores generated report context in memory.
    Prevents reloading from DB repeatedly.
    """
    _PATIENT_CONTEXT_CACHE[patient_id] = context


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