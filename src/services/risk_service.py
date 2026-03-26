# src/services/risk_service.py
from src.services.inventory_service import get_all_products

CRITICAL_THRESHOLD = 0

def classify_product(product: dict) -> str:
    stock = product["stock"]
    reorder = product["reorder_level"]
    if stock == CRITICAL_THRESHOLD:
        return "CRITICAL"
    elif stock < reorder:
        return "HIGH_RISK"
    return "OK"

def get_risk_analysis() -> dict:
    inventory = get_all_products()
    critical, high_risk, ok = [], [], []
    for product in inventory:
        status = classify_product(product)
        product_with_status = {**product, "status": status}
        if status == "CRITICAL":
            critical.append(product_with_status)
        elif status == "HIGH_RISK":
            high_risk.append(product_with_status)
        else:
            ok.append(product_with_status)
    return {
        "critical": critical,
        "high_risk": high_risk,
        "ok": ok,
        "summary": {
            "total_products": len(inventory),
            "critical_count": len(critical),
            "high_risk_count": len(high_risk),
            "ok_count": len(ok),
        }
    }

def get_purchase_plan() -> list[dict]:
    inventory = get_all_products()
    plan = []
    for product in inventory:
        stock = product["stock"]
        reorder = product["reorder_level"]
        if stock < reorder:
            quantity_needed = reorder - stock
            estimated_cost = round(quantity_needed * product["price"], 2)
            plan.append({
                "product": product["name"],
                "current_stock": stock,
                "reorder_level": reorder,
                "suggested_order": quantity_needed,
                "unit_price": product["price"],
                "estimated_cost": estimated_cost,
            })
    plan.sort(key=lambda x: x["current_stock"])
    return plan