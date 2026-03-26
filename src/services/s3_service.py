# src/services/s3_service.py
import boto3
import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

BUCKET  = os.getenv("S3_BUCKET", "inventory-history-720412502759")
REGION  = os.getenv("AWS_REGION", "us-east-1")

s3 = boto3.client("s3", region_name=REGION)

def save_snapshot(inventory: list[dict]) -> dict:
    """
    Guarda un snapshot del inventario actual en S3.
    Ruta: snapshots/YYYY/MM/DD/inventory_HH-MM-SS.json
    """
    now       = datetime.now(timezone.utc)
    timestamp = now.strftime("%H-%M-%S")
    key       = f"snapshots/{now.strftime('%Y/%m/%d')}/inventory_{timestamp}.json"

    payload = {
        "timestamp": now.isoformat(),
        "product_count": len(inventory),
        "inventory": inventory
    }

    try:
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=json.dumps(payload, indent=2),
            ContentType="application/json"
        )
        logger.info(f"Snapshot saved to s3://{BUCKET}/{key}")
        return {"status": "ok", "key": key, "products": len(inventory)}

    except Exception as e:
        logger.error(f"S3 snapshot error: {e}")
        return {"status": "error", "message": str(e)}


def list_snapshots(limit: int = 10) -> list[dict]:
    """Lista los snapshots más recientes."""
    try:
        response = s3.list_objects_v2(
            Bucket=BUCKET,
            Prefix="snapshots/",
            MaxKeys=limit
        )
        objects = response.get("Contents", [])
        return [
            {
                "key":           obj["Key"],
                "size_kb":       round(obj["Size"] / 1024, 2),
                "last_modified": obj["LastModified"].isoformat()
            }
            for obj in sorted(objects, key=lambda x: x["LastModified"], reverse=True)
        ]
    except Exception as e:
        logger.error(f"S3 list error: {e}")
        return []