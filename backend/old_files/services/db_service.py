import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="report_data",
        user="postgres",
        password="ajw12345",
        port=5432
    )
