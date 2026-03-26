# src/utils/data_loader.py
import boto3
import logging
import os
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)

# Configuración — fácil de cambiar por región o tabla diferente
REGION     = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "inventory")
SOURCE     = os.getenv("DATA_SOURCE", "dynamodb")  # "dynamodb" o "json"

def load_inventory() -> list[dict]:
    """
    Carga inventario desde DynamoDB o JSON según DATA_SOURCE.
    El resto del sistema no sabe cuál se usa — eso es el punto.
    """
    if SOURCE == "json":
        return _load_from_json()
    return _load_from_dynamodb()


def _load_from_dynamodb() -> list[dict]:
    """
    Lee productos desde DynamoDB.
    Para cada producto: busca metadata + stock del día actual.
    """
    try:
        dynamodb = boto3.resource("dynamodb", region_name=REGION)
        table    = dynamodb.Table(TABLE_NAME)
        today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Paso 1: obtener todos los metadata
        metadata_response = table.scan(
            FilterExpression="record_type = :rt",
            ExpressionAttributeValues={":rt": "metadata"}
        )
        metadata_items = metadata_response.get("Items", [])

        if not metadata_items:
            logger.warning("No metadata items found in DynamoDB")
            return []

        # Paso 2: para cada producto, buscar su stock de hoy
        products = []
        for meta in metadata_items:
            product_id = meta["product_id"]

            stock_response = table.get_item(Key={
                "product_id": product_id,
                "record_type": f"stock#{today}"
            })
            stock_item = stock_response.get("Item", {})

            products.append({
                "name":          meta.get("name", "Unknown"),
                "price":         float(meta.get("price", 0)),
                "category":      meta.get("category", "general"),
                "stock":         int(stock_item.get("stock", 0)),
                "reorder_level": int(stock_item.get("reorder_level", 0)),
            })

        logger.info(f"Loaded {len(products)} products from DynamoDB")
        return products

    except Exception as e:
        logger.error(f"DynamoDB error: {e} — falling back to JSON")
        return _load_from_json()  # fallback automático si DynamoDB falla


def _load_from_json() -> list[dict]:
    """Fallback al JSON local — útil para desarrollo sin AWS."""
    import json
    DATA_PATH = os.getenv("INVENTORY_DATA_PATH", "data/inventory.json")
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        logger.error(f"JSON file not found: {DATA_PATH}")
        return []
    except Exception as e:
        logger.error(f"JSON load error: {e}")
        return []