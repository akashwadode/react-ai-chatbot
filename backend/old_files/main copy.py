from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.summary import router as summary_router
from backend.modules.chat.router import router as chat_router
from backend.routers.link import router as link_router

print("🚀 FASTAPI MAIN.PY LOADED")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTER ROUTERS HERE ONLY (GLOBAL LEVEL)

app.include_router(summary_router)
app.include_router(chat_router)
app.include_router(link_router)


@app.get("/test")
def test():
    print("🔥 TEST API HIT")
    return {"msg": "Backend Working"}

@app.get("/test-db")
def test_db():

    print("🔥 TEST DB HIT")

    from backend.services.db_service import get_connection

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        print("✅ DB CONNECTED")

        return {
            "status": "DB Connected",
            "result": result
        }

    except Exception as e:
        print("❌ DB ERROR:", e)
        return {"error": str(e)}

@app.get("/test-patient")
def test_patient():

    from backend.services.db_service import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Patient LIMIT 1;")
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    print("PATIENT:", data)

    return {"patient": str(data)}

@app.on_event("startup")
def show_routes():
    print("📢 REGISTERED ROUTES:")
    for route in app.routes:
        print(route.path)
