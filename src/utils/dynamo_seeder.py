# src/utils/dynamo_seeder.py
import boto3
import json
from datetime import datetime, timezone, timedelta

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("inventory")

def load_json():
    with open("data/inventory.json", "r") as f:
        return json.load(f)

def seed():
    inventory = load_json()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # TTL: 90 días desde hoy
    ttl_timestamp = int(
        (datetime.now(timezone.utc) + timedelta(days=90)).timestamp()
    )

    seeded = 0

    for product in inventory:
        name = product.get("name", "Unknown")
        product_id = f"product#{name.replace(' ', '_').upper()}"

        # Item 1: metadata del producto (no expira)
        table.put_item(Item={
            "product_id": product_id,
            "record_type": "metadata",
            "name": name,
            "price": str(product.get("price", 0)),
            "category": product.get("category", "general"),
        })

        # Item 2: stock del día (expira en 90 días)
        table.put_item(Item={
            "product_id": product_id,
            "record_type": f"stock#{today}",
            "stock": product.get("stock", 0),
            "reorder_level": product.get("reorder_level", 0),
            "ttl": ttl_timestamp,
        })

        seeded += 1
        print(f"  Seeded: {name} → {product_id}")

    print(f"\nDone. {seeded} products seeded ({seeded * 2} items in DynamoDB)")

if __name__ == "__main__":
    print("Seeding DynamoDB from inventory.json...\n")
    seed()