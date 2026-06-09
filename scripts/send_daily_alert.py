"""
OrderIQ — Daily Proactive Alert Script
Runs automatically via GitHub Actions every morning.
Loads order data, analyses it, and sends an email alert.
"""

import os
import sys

# Add project root to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_orders
from src.analyzer import analyse_orders
from src.emailer import send_alert_email


def main():
    print("OrderIQ Daily Alert — starting...")

    # Get recipient email from environment variable
    recipient = os.getenv("ALERT_EMAIL")
    if not recipient:
        print("No ALERT_EMAIL configured. Skipping alert.")
        return

    # Load and analyse order data
    print("Loading order data...")
    df = load_orders()
    df, summary, priorities = analyse_orders(df)

    print(f"Analysis complete:")
    print(f"  Total orders  : {summary['total_orders']}")
    print(f"  Overdue       : {summary['overdue_count']}")
    print(f"  Blocked       : {summary['blocked_count']}")
    print(f"  At Risk       : {summary['at_risk_count']}")
    print(f"  Value at Risk : ${summary['total_value_at_risk_aud']:,} AUD")

    # Only send if there are urgent orders
    urgent = (
        summary["overdue_count"] +
        summary["blocked_count"] +
        summary["at_risk_count"]
    )

    if urgent == 0:
        print("No urgent orders today. Skipping alert.")
        return

    # Send the email alert
    print(f"Sending alert to {recipient}...")
    success, message = send_alert_email(
        to_email=recipient,
        summary=summary,
        priorities=priorities,
    )

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ Failed: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()