def calculate_stock_risk(product):

    current_stock = product["current_stock"]
    reorder_level = product["reorder_level"]

    if current_stock == 0:
        return "CRITICAL"

    if current_stock < reorder_level:
        return "HIGH"

    if current_stock < reorder_level * 1.5:
        return "MEDIUM"

    return "LOW"


def calculate_inventory_value(inventory):

    total_value = 0

    for product in inventory:
        total_value += product["current_stock"] * product["price"]

    return total_value


def reorder_recommendations(inventory, top_n=10):

    recommendations = []

    for product in inventory:

        current_stock = product["current_stock"]
        reorder_level = product["reorder_level"]

        if current_stock < reorder_level:

            reorder_qty = reorder_level - current_stock

            recommendations.append({
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "category": product["category"],
                "current_stock": current_stock,
                "reorder_level": reorder_level,
                "recommended_reorder_qty": reorder_qty
            })

    recommendations = sorted(
        recommendations,
        key=lambda x: x["recommended_reorder_qty"],
        reverse=True
    )

    return recommendations[:top_n]


def risk_analysis(inventory):

    risk_products = []

    for product in inventory:

        risk = calculate_stock_risk(product)

        risk_products.append({
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "current_stock": product["current_stock"],
            "reorder_level": product["reorder_level"],
            "risk_level": risk
        })

    critical = [p for p in risk_products if p["risk_level"] == "CRITICAL"]
    high = [p for p in risk_products if p["risk_level"] == "HIGH"]

    return {
        "critical_products": critical,
        "high_risk_products": high,
        "total_critical": len(critical),
        "total_high_risk": len(high)
    }