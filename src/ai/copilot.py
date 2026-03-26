import requests

API_RECOMMENDATIONS = "http://127.0.0.1:8000/inventory/recommendations"
API_ANALYTICS = "http://127.0.0.1:8000/inventory/analytics"


def get_recommendations():
    response = requests.get(API_RECOMMENDATIONS)
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


def get_analytics():
    response = requests.get(API_ANALYTICS)
    data = response.json()

    total = data["total_products"]
    avg = round(data["average_stock"], 2)
    low = data["low_stock_products"]

    return (
        f"Inventory Analytics:\n"
        f"Total products: {total}\n"
        f"Average stock level: {avg}\n"
        f"Products with low stock: {low}"
    )


def copilot():

    print("\nAI Logistics Copilot")
    print("Type a question (or 'exit' to quit)\n")

    while True:

        user_input = input("You: ").lower()

        if user_input == "exit":
            break

        if "reorder" in user_input or "restock" in user_input:
            result = get_recommendations()

        elif "analytics" in user_input or "inventory" in user_input:
            result = get_analytics()

        else:
            result = "I can help with inventory analytics or restocking recommendations."

        print("\nAI:", result, "\n")


if __name__ == "__main__":
    copilot()