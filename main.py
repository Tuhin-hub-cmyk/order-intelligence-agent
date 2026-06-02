from src.data_loader import load_orders
from src.analyzer import analyse_orders


def main():

    # Load orders from CSV
    df = load_orders()
    print(f"\n✓ Loaded {len(df)} orders from SAP export")

    # Run automated analysis
    df, summary, priorities = analyse_orders(df)
    print(f"✓ Analysis complete\n")

    # Print the summary dashboard
    print("=" * 40)
    print("       ORDER SUMMARY — TODAY")
    print("=" * 40)
    print(f"  Total Orders    : {summary['total_orders']}")
    print(f"  Overdue         : {summary['overdue_count']}")
    print(f"  Blocked         : {summary['blocked_count']}")
    print(f"  At Risk         : {summary['at_risk_count']}")
    print(f"  Stale           : {summary['stale_count']}")
    print(f"  On Track        : {summary['on_track_count']}")
    print(f"  Completed       : {summary['completed_count']}")
    print(f"  Value at Risk   : ${summary['total_value_at_risk_aud']:,} AUD")
    print("=" * 40)

    # Print today's top 5 priorities
    print("\n  TODAY'S TOP PRIORITIES\n")
    for i, order in enumerate(priorities, 1):
        print(f"  {i}. [{order['flag']}] {order['order_id']} — {order['customer_name']}")
        print(f"     Status  : {order['status']}")
        print(f"     Due     : {order['days_until_due']} days")
        print(f"     Owner   : {order['assigned_to']}")
        if order["delay_reason"]:
            print(f"     Reason  : {order['delay_reason']}")
        print()


if __name__ == "__main__":
    main()