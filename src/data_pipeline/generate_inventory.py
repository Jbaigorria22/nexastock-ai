import random

def generate_inventory(n_products=1000):

    categories = ["Electronics", "Clothing", "Home", "Sports", "Toys"]

    inventory = []

    for i in range(n_products):

        product = {
            "product_id": f"P{i+1:05}",
            "product_name": f"Product_{i+1}",
            "category": random.choice(categories),
            "current_stock": random.randint(0, 200),
            "reorder_level": random.randint(10, 50),
            "price": round(random.uniform(10, 500), 2)
        }

        inventory.append(product)

    return inventory


inventory = generate_inventory(1048)