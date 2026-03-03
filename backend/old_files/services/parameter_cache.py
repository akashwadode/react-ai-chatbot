from backend.services.db_service import get_connection

PARAMETERS = []

def load_parameters_once():

    global PARAMETERS

    if PARAMETERS:
        return PARAMETERS

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT LOWER(ParameterName)
        FROM TestParameter
    """)

    rows = cursor.fetchall()

    PARAMETERS = [r[0] for r in rows]

    cursor.close()
    conn.close()

    print("✅ PARAMETERS LOADED:", PARAMETERS)

    return PARAMETERS
