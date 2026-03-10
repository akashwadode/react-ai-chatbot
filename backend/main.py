from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.report.report_router import router as summary_router
from modules.chat.chat_router import router as chat_router
from modules.link.link_router import router as link_router
from core.database import get_connection
from modules.whatsapp.whatsapp_router import router as whatsapp_router

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
app.include_router(whatsapp_router)



@app.on_event("startup")
def show_routes():
    print("📢 REGISTERED ROUTES:")
    for route in app.routes:
        print(route.path)