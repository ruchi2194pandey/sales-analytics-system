import os
import csv


# -------------------------------------------------
# Task 1.1: Read sales data with encoding handling
# -------------------------------------------------
def read_sales_data(filename):
    encodings = ["utf-8", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as file:
                lines = file.readlines()

            # Skip header and empty lines
            return [line.strip() for line in lines[1:] if line.strip()]

        except FileNotFoundError:
            print(f" Error: File not found -> {filename}")
            return []

        except UnicodeDecodeError:
            continue

    print(" Error: Unable to decode file with supported encodings.")
    return []


# -------------------------------------------------
# Task 1.2: Parse and clean data
# -------------------------------------------------
def normalize_product_name(product_name):
    """
    Mouse,Wireless -> Wireless Mouse
    """
    if not product_name:
        return None

    parts = [p.strip() for p in product_name.split(",") if p.strip()]
    return " ".join(parts)


def parse_transactions(raw_lines):
    transactions = []

    for line in raw_lines:
        fields = line.split("|")

        if len(fields) != 8:
            continue

        (
            transaction_id,
            date,
            product_id,
            product_name,
            quantity,
            unit_price,
            customer_id,
            region
        ) = fields

        try:
            transactions.append({
                "TransactionID": transaction_id.strip(),
                "Date": date.strip(),
                "ProductID": product_id.strip(),
                "ProductName": normalize_product_name(product_name),
                "Quantity": int(quantity.replace(",", "").strip()),
                "UnitPrice": float(unit_price.replace(",", "").strip()),
                "CustomerID": customer_id.strip(),
                "Region": region.strip()
            })
        except (ValueError, AttributeError):
            continue

    return transactions


# -------------------------------------------------
# Task 1.3: Validation & Filtering
# -------------------------------------------------
def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    valid_transactions = []
    invalid_count = 0

    available_regions = set()
    amounts = []

    for tx in transactions:
        # Required field validation
        if not all([
            tx.get("TransactionID"),
            tx.get("ProductID"),
            tx.get("CustomerID"),
            tx.get("Region")
        ]):
            invalid_count += 1
            continue

        # ID rules
        if not (
            tx["TransactionID"].startswith("T")
            and tx["ProductID"].startswith("P")
            and tx["CustomerID"].startswith("C")
        ):
            invalid_count += 1
            continue

        # Value rules
        if tx["Quantity"] <= 0 or tx["UnitPrice"] <= 0:
            invalid_count += 1
            continue

        amount = tx["Quantity"] * tx["UnitPrice"]
        available_regions.add(tx["Region"])
        amounts.append(amount)

        valid_transactions.append(tx)

    # Display filter info
    print("\n Available Regions:", sorted(available_regions))
    if amounts:
        print(f" Transaction Amount Range: {min(amounts)} - {max(amounts)}")

    filtered = valid_transactions[:]
    filtered_by_region = 0
    filtered_by_amount = 0

    if region:
        before = len(filtered)
        filtered = [tx for tx in filtered if tx["Region"] == region]
        filtered_by_region = before - len(filtered)
        print(f" After region filter ({region}): {len(filtered)} records")

    if min_amount is not None:
        before = len(filtered)
        filtered = [
            tx for tx in filtered
            if tx["Quantity"] * tx["UnitPrice"] >= min_amount
        ]
        filtered_by_amount += before - len(filtered)

    if max_amount is not None:
        before = len(filtered)
        filtered = [
            tx for tx in filtered
            if tx["Quantity"] * tx["UnitPrice"] <= max_amount
        ]
        filtered_by_amount += before - len(filtered)

    summary = {
        "total_input": len(transactions),
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered)
    }

    return filtered, invalid_count, summary


# -------------------------------------------------
# Existing output: pipe-delimited TXT
# -------------------------------------------------
def write_cleaned_txt(transactions, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(
            "TransactionID|Date|ProductID|ProductName|"
            "Quantity|UnitPrice|CustomerID|Region\n"
        )

        for tx in transactions:
            file.write(
                f"{tx['TransactionID']}|{tx['Date']}|{tx['ProductID']}|"
                f"{tx['ProductName']}|{tx['Quantity']}|{tx['UnitPrice']}|"
                f"{tx['CustomerID']}|{tx['Region']}\n"
            )


# -------------------------------------------------
# NEW STEP: Generate cleaned CSV file
# -------------------------------------------------
def write_cleaned_csv(transactions, output_file):
    headers = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(transactions)


# -------------------------------------------------
# Main Execution
# -------------------------------------------------
if __name__ == "__main__":
    INPUT_FILE = os.path.join("data", "sales_data.txt")


    OUTPUT_CSV = os.path.join("output", "cleaned_sales_data.csv")

    raw_data = read_sales_data(INPUT_FILE)
    parsed_data = parse_transactions(raw_data)

    valid_data, invalid_count, summary = validate_and_filter(parsed_data)

 
    # NEW additional output
    write_cleaned_csv(valid_data, OUTPUT_CSV)

    print("\n Processing completed")
    print(f" CSV Output : {OUTPUT_CSV}")

    print("\n Summary:")
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("\n Sample Records:")
    for tx in valid_data[:5]:
        print(tx)
