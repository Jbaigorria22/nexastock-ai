# src/services/inventory_service.py
from src.utils.data_loader import load_inventory


def get_all_products() -> list[dict]:
    """Devuelve todos los productos con campos normalizados."""
    inventory = load_inventory()
    normalized = []
    for item in inventory:
        normalized.append({
            "name": item.get("name", "Unknown"),
            "stock": max(0, int(item.get("stock", 0))),
            "reorder_level": max(0, int(item.get("reorder_level", 0))),
            "price": max(0.0, float(item.get("price", 0.0))),
        })
    return normalized


def build_context(inventory: list[dict]) -> str:
    """
    Genera el contexto de texto para los prompts de IA.
    Centralizado aquí para que todos los endpoints de IA
    usen exactamente el mismo formato.
    """
    lines = []
    for p in inventory:
        lines.append(
            f"{p['name']} | Stock: {p['stock']} | "
            f"Reorder Level: {p['reorder_level']} | Price: ${p['price']:.2f}"
        )
    return "\n".join(lines)