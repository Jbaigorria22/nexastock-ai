import boto3
from pathlib import Path

bucket_name = "ai-logistics-datalake"
s3_key = "processed/sales_cleaned/sales_cleaned.parquet"

local_file = Path("data/processed/sales_cleaned.parquet")

s3 = boto3.client("s3")

try:
    s3.upload_file(str(local_file), bucket_name, s3_key)
    print("Upload completed successfully.")
except Exception as e:
    print("Upload failed:", e)