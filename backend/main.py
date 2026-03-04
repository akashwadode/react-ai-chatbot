from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.report.router import router as summary_router
from modules.chat.router import router as chat_router
from modules.link.router import router as link_router
from core.database import get_connection


print("🚀 FASTAPI MAIN.PY LOADED")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTER MODULE ROUTERS
app.include_router(summary_router)
app.include_router(chat_router)
app.include_router(link_router)


@app.get("/test")
def test():
    return {"msg": "Backend Working"}


@app.get("/test-db")
def test_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return {"status": "DB Connected", "result": result}

    except Exception as e:
        return {"error": str(e)}


@app.get("/test-patient")
def test_patient():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Patient LIMIT 1;")
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"patient": str(data)}


@app.on_event("startup")
def show_routes():
    print("📢 REGISTERED ROUTES:")
    for route in app.routes:
        print(route.path)