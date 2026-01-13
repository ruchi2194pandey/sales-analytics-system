import csv
import os
import requests

API_URL = "https://dummyjson.com/products?limit=100"

# ============================================================
# 1. Fetch API products
# ============================================================

def fetch_all_products():
    """
    Fetches products from DummyJSON API
    """
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        print(f"SUCCESS: Fetched {len(products)} products from API")
        # Use .get() to avoid KeyErrors
        return [
            {
                "id": p.get("id"),
                "title": p.get("title", "Unknown Product"),
                "category": p.get("category", None),
                "brand": p.get("brand", None),
                "rating": p.get("rating", None)
            }
            for p in products
        ]
    except requests.RequestException as e:
        print("ERROR: Failed to fetch API products:", e)
        return []

# ============================================================
# 2. Create mapping from numeric ID → product info
# ============================================================

def create_product_mapping(api_products):
    mapping = {}
    for p in api_products:
        if p.get("id") is not None:
            mapping[p["id"]] = p
    return mapping

# ============================================================
# 3. Enrich transactions
# ============================================================

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    """
    enriched = []

    for tx in transactions:
        tx_enriched = tx.copy()
        api_product = None

        # Extract numeric ID from ProductID (P101 -> 101)
        try:
            numeric_id = int("".join(filter(str.isdigit, tx["ProductID"])))
            api_product = product_mapping.get(numeric_id)
        except ValueError:
            api_product = None

        # Set API fields
        if api_product:
            tx_enriched["API_Category"] = api_product.get("category")
            tx_enriched["API_Brand"] = api_product.get("brand")
            tx_enriched["API_Rating"] = api_product.get("rating")
            tx_enriched["API_Match"] = True
        else:
            tx_enriched["API_Category"] = None
            tx_enriched["API_Brand"] = None
            tx_enriched["API_Rating"] = None
            tx_enriched["API_Match"] = False

        enriched.append(tx_enriched)

    # Save to file
    save_enriched_data(enriched)

    return enriched

# ============================================================
# 4. Save enriched data to pipe-delimited file
# ============================================================

def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    if not enriched_transactions:
        print("WARNING: No data to save")
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(headers)
        for tx in enriched_transactions:
            row = []
            for h in headers:
                value = tx.get(h)
                # Keep None as literal "None", booleans stay as True/False
                if value is None:
                    value = "None"
                row.append(value)
            writer.writerow(row)

    print(f"SUCCESS: Enriched data saved to {filename}")

# ============================================================
# 5. Usage / main
# ============================================================

def main():
    # Load cleaned sales data
    transactions = []
    try:
        with open("output/cleaned_sales_data.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transactions.append({
                    "TransactionID": row["TransactionID"],
                    "Date": row["Date"],
                    "ProductID": row["ProductID"],
                    "ProductName": row["ProductName"],
                    "Quantity": int(row["Quantity"]),
                    "UnitPrice": float(row["UnitPrice"]),
                    "CustomerID": row["CustomerID"],
                    "Region": row["Region"]
                })
    except FileNotFoundError:
        print("ERROR: cleaned_sales_data.csv not found")
        return

    # Fetch API data and create mapping
    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)

    # Enrich and save
    enriched_transactions = enrich_sales_data(transactions, product_mapping)

    # Print sample
    print("\nSample enriched transaction:")
    print(enriched_transactions[0])

if __name__ == "__main__":
    main()
