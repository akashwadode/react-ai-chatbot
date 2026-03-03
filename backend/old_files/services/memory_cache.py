PATIENT_MEMORY_CACHE = {}

def get_memory(patient_id):
    return PATIENT_MEMORY_CACHE.setdefault(patient_id, [])
