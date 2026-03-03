PATIENT_CONTEXT_CACHE = {}

def get_cached_context(patient_id):
    return PATIENT_CONTEXT_CACHE.get(patient_id)

def set_cached_context(patient_id, context):
    PATIENT_CONTEXT_CACHE[patient_id] = context
