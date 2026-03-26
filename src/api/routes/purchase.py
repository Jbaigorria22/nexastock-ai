# src/api/routes/purchase.py
from fastapi import APIRouter
from src.services.risk_service import get_purchase_plan

router = APIRouter()

@router.get("/plan")
def purchase_plan():
    plan = get_purchase_plan()
    total_cost = sum(item["estimated_cost"] for item in plan)
    return {
        "plan": plan,
        "total_estimated_cost": round(total_cost, 2),
        "items_to_reorder": len(plan),
    }