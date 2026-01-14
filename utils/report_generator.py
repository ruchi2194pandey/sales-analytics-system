import os
from datetime import datetime
from collections import defaultdict

# =====================================================
# BASIC CALCULATIONS
# =====================================================

def calculate_total_revenue(transactions):
    return sum(t["Quantity"] * t["UnitPrice"] for t in transactions)

def region_wise_sales(transactions):
    data = defaultdict(lambda: {"sales": 0.0, "count": 0})

    for t in transactions:
        revenue = t["Quantity"] * t["UnitPrice"]
        data[t["Region"]]["sales"] += revenue
        data[t["Region"]]["count"] += 1

    total_sales = sum(v["sales"] for v in data.values())
    result = []

    for region, v in data.items():
        percent = (v["sales"] / total_sales * 100) if total_sales else 0
        result.append((region, v["sales"], percent, v["count"]))

    return sorted(result, key=lambda x: x[1], reverse=True)

def daily_sales_trend(transactions):
    daily = defaultdict(lambda: {"revenue": 0.0, "count": 0, "customers": set()})

    for t in transactions:
        date = t["Date"]
        daily[date]["revenue"] += t["Quantity"] * t["UnitPrice"]
        daily[date]["count"] += 1
        daily[date]["customers"].add(t["CustomerID"])

    return dict(sorted(daily.items()))

def top_products(transactions, n=5):
    products = defaultdict(lambda: {"qty": 0, "revenue": 0.0})

    for t in transactions:
        products[t["ProductName"]]["qty"] += t["Quantity"]
        products[t["ProductName"]]["revenue"] += t["Quantity"] * t["UnitPrice"]

    sorted_products = sorted(
        products.items(),
        key=lambda x: x[1]["qty"],
        reverse=True
    )

    return [(i + 1, p, v["qty"], v["revenue"]) for i, (p, v) in enumerate(sorted_products[:n])]

def top_customers(transactions, n=5):
    customers = defaultdict(lambda: {"spent": 0.0, "count": 0})

    for t in transactions:
        amt = t["Quantity"] * t["UnitPrice"]
        customers[t["CustomerID"]]["spent"] += amt
        customers[t["CustomerID"]]["count"] += 1

    sorted_customers = sorted(
        customers.items(),
        key=lambda x: x[1]["spent"],
        reverse=True
    )

    return [(i + 1, c, v["spent"], v["count"]) for i, (c, v) in enumerate(sorted_customers[:n])]

# =====================================================
# API ENRICHMENT SUMMARY
# =====================================================

def api_enrichment_summary(enriched_transactions):
    total = len(enriched_transactions)
    matched = [t for t in enriched_transactions if t.get("API_Match") is True]
    failed = [t for t in enriched_transactions if t.get("API_Match") is False]

    failed_products = sorted(set(t["ProductName"] for t in failed))
    success_rate = (len(matched) / total * 100) if total else 0

    return {
        "total": total,
        "matched": len(matched),
        "failed": len(failed),
        "success_rate": success_rate,
        "failed_products": failed_products
    }

# =====================================================
# REPORT GENERATOR
# =====================================================

def generate_sales_report(transactions, enriched_transactions, output_file="output/sales_report.txt"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    total_revenue = calculate_total_revenue(transactions)
    avg_order = total_revenue / len(transactions)
    dates = sorted(t["Date"] for t in transactions)

    with open(output_file, "w", encoding="utf-8") as f:

        # HEADER
        f.write("=" * 60 + "\n")
        f.write("               SALES ANALYTICS REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Records Processed: {len(transactions)}\n")
        f.write("=" * 60 + "\n\n")

        # OVERALL SUMMARY
        f.write("OVERALL SUMMARY\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions:   {len(transactions)}\n")
        f.write(f"Average Order Value:  ₹{avg_order:,.2f}\n")
        f.write(f"Date Range:           {dates[0]} to {dates[-1]}\n\n")

        # REGION PERFORMANCE
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Region':<10}{'Sales':>15}{'%Total':>12}{'Txns':>10}\n")

        for r, s, p, c in region_wise_sales(transactions):
            f.write(f"{r:<10}₹{s:>14,.2f}{p:>11.2f}%{c:>10}\n")

        f.write("\n")

        # TOP PRODUCTS
        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Rank':<6}{'Product':<20}{'Qty':>8}{'Revenue':>15}\n")

        for r, p, q, rev in top_products(transactions):
            f.write(f"{r:<6}{p:<20}{q:>8}₹{rev:>14,.2f}\n")

        f.write("\n")

        # TOP CUSTOMERS
        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Rank':<6}{'Customer':<15}{'Spent':>15}{'Orders':>10}\n")

        for r, c, s, o in top_customers(transactions):
            f.write(f"{r:<6}{c:<15}₹{s:>14,.2f}{o:>10}\n")

        f.write("\n")

        # DAILY TREND
        f.write("DAILY SALES TREND\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'Date':<12}{'Revenue':>15}{'Txns':>8}{'Customers':>12}\n")

        for d, v in daily_sales_trend(transactions).items():
            f.write(f"{d:<12}₹{v['revenue']:>14,.2f}{v['count']:>8}{len(v['customers']):>12}\n")

        f.write("\n")

        # API ENRICHMENT SUMMARY
        summary = api_enrichment_summary(enriched_transactions)

        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total Transactions Checked: {summary['total']}\n")
        f.write(f"Successfully Enriched:      {summary['matched']}\n")
        f.write(f"Failed Enrichments:         {summary['failed']}\n")
        f.write(f"Success Rate:               {summary['success_rate']:.2f}%\n\n")

        f.write("Products Without API Match:\n")
        if summary["failed_products"]:
            for p in summary["failed_products"]:
                f.write(f" - {p}\n")
        else:
            f.write(" None\n")

    print(f"SUCCESS: Report generated at -> {output_file}")

# =====================================================
# USAGE / ENTRY POINT
# =====================================================

if __name__ == "__main__":

    # SAMPLE DATA (replace with real cleaned + enriched data)
    transactions = [
        {
            "TransactionID": "T001",
            "Date": "2024-12-01",
            "ProductID": "P101",
            "ProductName": "Laptop",
            "Quantity": 2,
            "UnitPrice": 45000.0,
            "CustomerID": "C001",
            "Region": "North"
        }
    ]

    enriched_transactions = [
        {
            **transactions[0],
            "API_Category": None,
            "API_Brand": None,
            "API_Rating": None,
            "API_Match": False
        }
    ]

    generate_sales_report(transactions, enriched_transactions)
