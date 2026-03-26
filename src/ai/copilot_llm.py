import requests
from openai import OpenAI

client = OpenAI()

API_BASE = "http://127.0.0.1:8000"


def get_inventory_analytics():
    r = requests.get(f"{API_BASE}/inventory/analytics")
    return r.json()


def get_risk_analysis():
    r = requests.get(f"{API_BASE}/inventory/risk-analysis")
    return r.json()


def get_reorder_recommendations():
    r = requests.get(f"{API_BASE}/inventory/reorder-recommendations")
    return r.json()


def build_context():

    analytics = get_inventory_analytics()
    risk = get_risk_analysis()
    reorder = get_reorder_recommendations()

    context = f"""
Inventory Analytics:
Total products: {analytics['total_products']}
Average stock: {analytics['average_stock']}
Low stock products: {analytics['low_stock_products']}

Risk Summary:
Critical products: {risk['risk_summary']['total_critical']}
High risk products: {risk['risk_summary']['total_high_risk']}

Inventory Value:
{risk['inventory_value']}

Top Reorder Recommendations:
{reorder['top_reorder_recommendations']}
"""

    return context


def copilot():

    print("AI Logistics Copilot")
    print("Type a question or 'exit'\n")

    context = build_context()

    while True:

        question = input("You: ")

        if question.lower() == "exit":
            break

        prompt = f"""
You are an AI logistics analyst.

Use the following inventory data to answer the user question.

{context}

User Question:
{question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a supply chain AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        print("\nAI:", response.choices[0].message.content, "\n")


if __name__ == "__main__":
    copilot()