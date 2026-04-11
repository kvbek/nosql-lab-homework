import sys
import os
import random
import psycopg2
from psycopg2.extras import execute_batch


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.embedding import embed


# =========================
# CONFIG
# =========================
DB_CONFIG = {
    "host": "pgvector_snoql_lab",
    "database": "vectordb",
    "user": "user",
    "password": "password"
}

N_PRODUCTS = 5000
BATCH_SIZE = 200
SEED = 42

random.seed(SEED)


# =========================
# DATA GENERATION
# =========================
CATEGORIES = {
    "electronics": {
        "products": ["headphones", "speaker", "laptop", "smartphone"],
        "features": ["wireless", "noise cancelling", "bluetooth", "high performance"]
    },
    "sports": {
        "products": ["running shoes", "fitness tracker", "dumbbells"],
        "features": ["lightweight", "durable", "ergonomic", "comfortable"]
    },
    "home": {
        "products": ["coffee machine", "vacuum cleaner", "air purifier"],
        "features": ["compact", "energy efficient", "quiet", "modern"]
    },
    "fashion": {
        "products": ["jacket", "jeans", "sneakers"],
        "features": ["stylish", "casual", "premium", "comfortable"]
    }
}


def generate_product(i):
    category = random.choice(list(CATEGORIES.keys()))
    data = CATEGORIES[category]

    product = random.choice(data["products"])
    f1, f2 = random.sample(data["features"], 2)

    name = f"{f1.title()} {product.title()} {random.randint(100,999)}"
    description = f"{f1} {product} with {f2}, ideal for {category} use"

    return {
        "id": i,
        "name": name,
        "category": category,
        "price": random.randint(20, 1000),
        "description": description
    }


def generate_batch(start_id, size):
    return [generate_product(i) for i in range(start_id, start_id + size)]


# =========================
# DB LOAD
# =========================
def generate():
    print("Connecting to DB...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"Generating {N_PRODUCTS} products...")

    current_id = 1

    for batch_start in range(0, N_PRODUCTS, BATCH_SIZE):
        batch = generate_batch(current_id, BATCH_SIZE)
        current_id += BATCH_SIZE

        descriptions = [p["description"] for p in batch]
        vectors = embed(descriptions)

        rows = []
        for p, vec in zip(batch, vectors):
            rows.append((
                p["id"],
                p["name"],
                p["category"],
                p["price"],
                p["description"],
                vec.tolist()
            ))

        execute_batch(
            cur,
            """
            INSERT INTO products (id, name, category, price, description, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            rows,
            page_size=BATCH_SIZE
        )

        print(f"Inserted batch {batch_start + BATCH_SIZE}/{N_PRODUCTS}")

    conn.commit()

    # =========================
    # SALES GENERATION
    # =========================
    print("Generating sales data...")

    sales_rows = [
        (i, random.randint(10, 5000))
        for i in range(1, N_PRODUCTS + 1)
    ]

    execute_batch(
        cur,
        """
        INSERT INTO sales (product_id, sales_count)
        VALUES (%s, %s)
        """,
        sales_rows,
        page_size=BATCH_SIZE
    )

    conn.commit()
    conn.close()

    print("DONE")


if __name__ == "__main__":
    generate()