"""
OrderIQ — Daily Proactive Alert Script
Runs automatically via GitHub Actions every weekday morning.
"""

import os
import sys
import pandas as pd

# Add project root to Python path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.data_loader import load_orders
from src.analyzer import analyse_orders
from src.emailer import send_alert_email


def main():
    print("=" * 45)
    print("  OrderIQ Daily Alert — starting")
    print("=" * 45)

    # Check secrets are available
    resend_key = os.getenv("RESEND_API_KEY")
    recipient  = os.getenv("ALERT_EMAIL")

    if not resend_key:
        print("✗ RESEND_API_KEY secret not found.")
        print("  Add it in GitHub → Settings → Secrets → Actions")
        sys.exit(1)

    if not recipient:
        print("✗ ALERT_EMAIL secret not found.")
        print("  Add it in GitHub → Settings → Secrets → Actions")
        sys.exit(1)

    print(f"✓ Sending to: {recipient}")

    # Load and analyse order data
    print("\nLoading order data...")
    try:
        df = load_orders()
        df, summary, priorities = analyse_orders(df)
    except Exception as e:
        print(f"✗ Failed to load data: {e}")
        sys.exit(1)

    print(f"✓ Loaded {summary['total_orders']} orders")
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
        print("\n✓ No urgent orders today — skipping alert.")
        return

    # Send the email
    print(f"\nSending alert ({urgent} urgent orders)...")
    try:
        success, message = send_alert_email(
            to_email=recipient,
            summary=summary,
            priorities=priorities,
        )
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Email failed: {e}")
        sys.exit(1)

    print("\n✓ Daily alert complete.")


if __name__ == "__main__":
    main()