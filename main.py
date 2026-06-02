from src.data_loader import load_orders


def main():
    # Load the orders
    df = load_orders()

    # Confirm how many rows loaded
    print(f"\n✓ Loaded {len(df)} orders from SAP export\n")

    # Show the key columns for every order
    display_cols = [
        "order_id",
        "customer_name",
        "status",
        "priority",
        "due_date",
        "days_until_due",
        "assigned_to",
    ]
    print(df[display_cols].to_string(index=False))

    # Separate section — show just the overdue orders
    overdue = df[
        (df["days_until_due"] < 0) &
        (df["status"] != "Completed")
    ]

    print(f"\n--- OVERDUE ORDERS ({len(overdue)} found) ---\n")
    print(
        overdue[["order_id", "customer_name", "status", "days_until_due", "delay_reason"]]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()