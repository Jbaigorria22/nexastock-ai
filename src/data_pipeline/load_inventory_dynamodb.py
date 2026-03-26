import boto3
import pandas as pd

# Conectar con DynamoDB
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("Inventory")

# Leer dataset procesado
df = pd.read_parquet("data/processed/sales_cleaned.parquet")

# Obtener productos únicos
products = df[["product_id"]].drop_duplicates().head(50)
# Insertar inventario inicial
for i, (_, row) in enumerate(products.iterrows(), start=1):

    item = {
        "product_id": str(row["product_id"]),
        "warehouse_id": "WH-001",
        "stock_quantity": 100,
        "reorder_level": 20
    }

    table.put_item(Item=item)

    print(f"Inserted item {i}")