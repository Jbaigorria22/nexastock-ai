# src/api/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Crear app PRIMERO
app = FastAPI(
    title="AI Inventory Decision Dashboard",
    description="Inventory management API with AI-powered insights",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers DESPUÉS de crear app
from src.api.routes.inventory import router as inventory_router
from src.api.routes.risk import router as risk_router
from src.api.routes.ai import router as ai_router
from src.api.routes.purchase import router as purchase_router
from src.api.routes.storage import router as storage_router

# Registrar routers
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(risk_router,      prefix="/risk",      tags=["Risk"])
app.include_router(ai_router,        prefix="/ai",        tags=["AI"])
app.include_router(purchase_router,  prefix="/purchase",  tags=["Purchase"])
app.include_router(storage_router,   prefix="/storage",   tags=["Storage"])


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "AI Inventory Dashboard API",
        "version": "1.0.0"
    }


# ── Aliases de compatibilidad (rutas viejas) ───────────────────────────────────
from src.services.inventory_service import get_all_products
from src.services.risk_service import get_risk_analysis, get_purchase_plan
from src.services.ai_service import get_ai_summary, get_copilot_answer


class QuestionCompat(BaseModel):
    question: str


@app.get("/inventory")
def compat_inventory():
    return get_all_products()


@app.get("/risk-analysis")
def compat_risk():
    return get_risk_analysis()


@app.get("/purchase-plan")
def compat_purchase():
    plan = get_purchase_plan()
    total = 0.0
    for item in plan:
        total += float(item.get("estimated_cost", 0))
    return {"plan": plan, "total_estimated_cost": round(total, 2)}


@app.get("/ai-summary")
def compat_summary():
    return get_ai_summary()


@app.post("/copilot")
def compat_copilot(q: QuestionCompat):
    return get_copilot_answer(q.question)

# Handler para AWS Lambda
from mangum import Mangum
handler = Mangum(app)