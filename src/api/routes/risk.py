# src/api/routes/risk.py
from fastapi import APIRouter
from src.services.risk_service import get_risk_analysis

router = APIRouter()

@router.get("/analysis")
def risk_analysis():
    return get_risk_analysis()