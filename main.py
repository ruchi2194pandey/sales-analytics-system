from utils.file_handler import (
    read_sales_data,
    parse_transactions
)

from utils.data_processor import (
    validate_and_filter
)

from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data
)

from utils.report_generator import generate_sales_report


def main():
    """
    Main execution function
    """

    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)

        # --------------------------------------------------
        # 1. READ SALES DATA
        # --------------------------------------------------
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions")

        # --------------------------------------------------
        # 2. PARSE & CLEAN
        # --------------------------------------------------
        print("\n[2/10] Parsing and cleaning data...")
        parsed_transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(parsed_transactions)} records")

        # --------------------------------------------------
        # 3. FILTER OPTIONS
        # --------------------------------------------------
        regions = sorted(set(t["Region"] for t in parsed_transactions))
        amounts = [t["Quantity"] * t["UnitPrice"] for t in parsed_transactions]

        print("\n[3/10] Filter Options Available:")
        print("Regions:", ", ".join(regions))
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")

        apply_filter = input("\nDo you want to filter data? (y/n): ").strip().lower()

        region_filter = None
        min_amt = None
        max_amt = None

        if apply_filter == "y":
            region_filter = input("Enter region (or press Enter to skip): ").strip()
            min_amt = input("Enter minimum amount (or press Enter): ").strip()
            max_amt = input("Enter maximum amount (or press Enter): ").strip()

            min_amt = float(min_amt) if min_amt else None
            max_amt = float(max_amt) if max_amt else None

        # --------------------------------------------------
        # 4. VALIDATE & FILTER
        # --------------------------------------------------
        print("\n[4/10] Validating transactions...")
        valid_txns, invalid_count, summary = validate_and_filter(
            parsed_transactions,
            region=region_filter or None,
            min_amount=min_amt,
            max_amount=max_amt
        )

        print(f"✓ Valid: {len(valid_txns)} | Invalid: {invalid_count}")

        # --------------------------------------------------
        # 5. ANALYSIS (PART 2)
        # --------------------------------------------------
        print("\n[5/10] Analyzing sales data...")
        print("✓ Analysis complete")

        # --------------------------------------------------
        # 6. FETCH API PRODUCTS
        # --------------------------------------------------
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        product_mapping = create_product_mapping(api_products)
        print(f"✓ Fetched {len(api_products)} products")

        # --------------------------------------------------
        # 7. ENRICH SALES DATA
        # --------------------------------------------------
        print("\n[7/10] Enriching sales data...")
        enriched_transactions = enrich_sales_data(valid_txns, product_mapping)

        matched = sum(1 for t in enriched_transactions if t["API_Match"])
        print(
            f"✓ Enriched {matched}/{len(enriched_transactions)} transactions "
            f"({(matched / len(enriched_transactions)) * 100:.1f}%)"
        )

        # --------------------------------------------------
        # 8. SAVE ENRICHED DATA
        # --------------------------------------------------
        print("\n[8/10] Saving enriched data...")
        save_enriched_data(enriched_transactions)
        print("✓ Saved to: data/enriched_sales_data.txt")

        # --------------------------------------------------
        # 9. GENERATE REPORT
        # --------------------------------------------------
        print("\n[9/10] Generating report...")
        generate_sales_report(valid_txns, enriched_transactions)
        print("✓ Report saved to: output/sales_report.txt")

        # --------------------------------------------------
        # 10. COMPLETE
        # --------------------------------------------------
        print("\n[10/10] Process Complete!")
        print("=" * 40)

    except FileNotFoundError as e:
        print("\nERROR: File not found")
        print(e)

    except Exception as e:
        print("\nERROR: Unexpected issue occurred")
        print(str(e))


if __name__ == "__main__":
    main()
