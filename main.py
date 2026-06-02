from src.data_loader import load_orders
from src.analyzer import analyse_orders
from src.agent import ask_agent


def print_dashboard(summary: dict, priorities: list) -> None:
    """Print the order summary dashboard to the terminal."""

    print("\n" + "=" * 50)
    print("    ATLAS COPCO — ORDER INTELLIGENCE AGENT")
    print("=" * 50)
    print(f"  Total Orders    : {summary['total_orders']}")
    print(f"  Overdue         : {summary['overdue_count']}")
    print(f"  Blocked         : {summary['blocked_count']}")
    print(f"  At Risk         : {summary['at_risk_count']}")
    print(f"  Stale           : {summary['stale_count']}")
    print(f"  On Track        : {summary['on_track_count']}")
    print(f"  Completed       : {summary['completed_count']}")
    print(f"  Value at Risk   : ${summary['total_value_at_risk_aud']:,} AUD")
    print("=" * 50)

    print("\n  TODAY'S TOP PRIORITIES\n")
    for i, order in enumerate(priorities, 1):
        print(
            f"  {i}. [{order['flag']}] "
            f"{order['order_id']} — {order['customer_name']}"
        )
        print(f"     Status  : {order['status']}")
        print(f"     Due     : {order['days_until_due']} days")
        print(f"     Owner   : {order['assigned_to']}")
        if order["delay_reason"]:
            print(f"     Reason  : {order['delay_reason']}")
        print()

    print("-" * 50)
    print("  Type a question about your orders below.")
    print("  Commands: 'refresh' to reload | 'quit' to exit")
    print("-" * 50 + "\n")


def main():

    print("\n  Loading orders...\n")

    # Load data and run analysis
    df = load_orders()
    df, summary, priorities = analyse_orders(df)

    # Show the dashboard
    print_dashboard(summary, priorities)

    # Conversation history — persists across questions
    history = []

    # Interactive Q&A loop
    while True:
        try:
            question = input("  Ask: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Goodbye!\n")
            break

        # Skip empty input
        if not question:
            continue

        # Exit command
        if question.lower() == "quit":
            print("\n  Goodbye!\n")
            break

        # Refresh command — reload data and reset conversation
        if question.lower() == "refresh":
            print("\n  Refreshing data...\n")
            df = load_orders()
            df, summary, priorities = analyse_orders(df)
            print_dashboard(summary, priorities)
            history = []
            continue

        # Send question to AI agent
        print("\n  Thinking...\n")
        answer, history = ask_agent(question, df, summary, history)

        print("  " + "─" * 48)
        # Print answer with nice indentation
        for line in answer.split("\n"):
            print(f"  {line}")
        print("  " + "─" * 48 + "\n")


if __name__ == "__main__":
    main()