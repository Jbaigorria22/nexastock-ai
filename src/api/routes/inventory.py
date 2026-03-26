# src/api/routes/inventory.py
from fastapi import APIRouter
from src.services.inventory_service import get_all_products

router = APIRouter()

@router.get("/")
def get_inventory():
    return get_all_products()