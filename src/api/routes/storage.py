# src/api/routes/storage.py
from fastapi import APIRouter
from src.services.s3_service import save_snapshot, list_snapshots
from src.services.inventory_service import get_all_products

router = APIRouter()

@router.post("/snapshot")
def create_snapshot():
    """Guarda el estado actual del inventario en S3."""
    inventory = get_all_products()
    result    = save_snapshot(inventory)
    return result

@router.get("/snapshots")
def get_snapshots():
    """Lista los últimos snapshots guardados en S3."""
    return {"snapshots": list_snapshots()}