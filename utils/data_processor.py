import csv
from collections import defaultdict
from datetime import datetime


# ============================================================
# LOAD CLEANED DATA (FROM TASK 1 OUTPUT)
# ============================================================

def load_cleaned_transactions(filepath):
    transactions = []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

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
        print(f"ERROR: Cleaned file not found -> {filepath}")

    return transactions


# ============================================================
# TASK 2.1 – SALES SUMMARY
# ============================================================

def calculate_total_revenue(transactions):
    return round(sum(tx["Quantity"] * tx["UnitPrice"] for tx in transactions), 2)


def region_wise_sales(transactions):
    region_map = defaultdict(lambda: {"total_sales": 0.0, "transaction_count": 0})
    total_revenue = calculate_total_revenue(transactions)

    for tx in transactions:
        amount = tx["Quantity"] * tx["UnitPrice"]
        region_map[tx["Region"]]["total_sales"] += amount
        region_map[tx["Region"]]["transaction_count"] += 1

    result = {}
    for region, data in region_map.items():
        result[region] = {
            "total_sales": round(data["total_sales"], 2),
            "transaction_count": data["transaction_count"],
            "percentage": round((data["total_sales"] / total_revenue) * 100, 2)
        }

    return dict(sorted(result.items(), key=lambda x: x[1]["total_sales"], reverse=True))


def top_selling_products(transactions, n=5):
    product_map = defaultdict(lambda: {"quantity": 0, "revenue": 0.0})

    for tx in transactions:
        product_map[tx["ProductName"]]["quantity"] += tx["Quantity"]
        product_map[tx["ProductName"]]["revenue"] += tx["Quantity"] * tx["UnitPrice"]

    sorted_products = sorted(
        product_map.items(),
        key=lambda x: x[1]["quantity"],
        reverse=True
    )

    return [
        (name, data["quantity"], round(data["revenue"], 2))
        for name, data in sorted_products[:n]
    ]


def customer_analysis(transactions):
    customer_map = defaultdict(lambda: {
        "total_spent": 0.0,
        "purchase_count": 0,
        "products": set()
    })

    for tx in transactions:
        amount = tx["Quantity"] * tx["UnitPrice"]
        customer_map[tx["CustomerID"]]["total_spent"] += amount
        customer_map[tx["CustomerID"]]["purchase_count"] += 1
        customer_map[tx["CustomerID"]]["products"].add(tx["ProductName"])

    result = {}
    for cid, data in customer_map.items():
        result[cid] = {
            "total_spent": round(data["total_spent"], 2),
            "purchase_count": data["purchase_count"],
            "avg_order_value": round(data["total_spent"] / data["purchase_count"], 2),
            "products_bought": sorted(data["products"])
        }

    return dict(sorted(result.items(), key=lambda x: x[1]["total_spent"], reverse=True))


# ============================================================
# TASK 2.2 – DATE BASED ANALYSIS
# ============================================================

def daily_sales_trend(transactions):
    daily_map = defaultdict(lambda: {
        "revenue": 0.0,
        "transaction_count": 0,
        "customers": set()
    })

    for tx in transactions:
        amount = tx["Quantity"] * tx["UnitPrice"]
        daily_map[tx["Date"]]["revenue"] += amount
        daily_map[tx["Date"]]["transaction_count"] += 1
        daily_map[tx["Date"]]["customers"].add(tx["CustomerID"])

    result = {}
    for date, data in daily_map.items():
        result[date] = {
            "revenue": round(data["revenue"], 2),
            "transaction_count": data["transaction_count"],
            "unique_customers": len(data["customers"])
        }

    return dict(sorted(result.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")))


def find_peak_sales_day(transactions):
    daily = daily_sales_trend(transactions)
    date, metrics = max(daily.items(), key=lambda x: x[1]["revenue"])
    return date, metrics["revenue"], metrics["transaction_count"]


# ============================================================
# TASK 2.3 – PRODUCT PERFORMANCE
# ============================================================

def low_performing_products(transactions, threshold=10):
    product_map = defaultdict(lambda: {"quantity": 0, "revenue": 0.0})

    for tx in transactions:
        product_map[tx["ProductName"]]["quantity"] += tx["Quantity"]
        product_map[tx["ProductName"]]["revenue"] += tx["Quantity"] * tx["UnitPrice"]

    return sorted(
        [
            (name, data["quantity"], round(data["revenue"], 2))
            for name, data in product_map.items()
            if data["quantity"] < threshold
        ],
        key=lambda x: x[1]
    )


# ============================================================
# MAIN – COMPLETE OUTPUT
# ============================================================

def main(transactions):
    print("\n========== SALES ANALYTICS REPORT ==========\n")

    print("TOTAL REVENUE:")
    print(calculate_total_revenue(transactions))

    print("\nREGION-WISE SALES:")
    for region, stats in region_wise_sales(transactions).items():
        print(region, "=>", stats)

    print("\nTOP 5 SELLING PRODUCTS:")
    for item in top_selling_products(transactions):
        print(item)

    print("\nCUSTOMER ANALYSIS (TOP 5):")
    for cust, data in list(customer_analysis(transactions).items())[:5]:
        print(cust, "=>", data)

    print("\nDAILY SALES TREND:")
    for date, data in daily_sales_trend(transactions).items():
        print(date, "=>", data)

    print("\nPEAK SALES DAY:")
    print(find_peak_sales_day(transactions))

    print("\nLOW PERFORMING PRODUCTS:")
    for product in low_performing_products(transactions):
        print(product)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    cleaned_file = "output/cleaned_sales_data.csv"
    transactions = load_cleaned_transactions(cleaned_file)

    if transactions:
        main(transactions)
