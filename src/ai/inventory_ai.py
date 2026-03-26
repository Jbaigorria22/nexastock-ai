import requests

API_URL = "http://127.0.0.1:8000/inventory/recommendations"

def get_restock_recommendations():

    response = requests.get(API_URL)
    data = response.json()

    if not data:
        return "All products have sufficient stock."

    messages = []

    for item in data:

        product = item["product_id"]
        warehouse = item["warehouse_id"]
        stock = item["current_stock"]
        reorder = item["reorder_level"]
        recommended = item["recommended_order_quantity"]

        message = (
            f"Product {product} in warehouse {warehouse} "
            f"has stock {stock} below reorder level {reorder}. "
            f"Recommended order quantity: {recommended} units."
        )

        messages.append(message)

    return "\n".join(messages)


if __name__ == "__main__":

    result = get_restock_recommendations()

    print("\nAI Logistics Assistant\n")
    print(result)