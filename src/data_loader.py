import pandas as pd
from pathlib import Path


def load_orders() -> pd.DataFrame:
    """
    Load the mock SAP orders CSV and return a clean DataFrame.

    Parses all date columns and calculates:
    - days_until_due: days remaining until due date (negative = overdue)
    - days_since_update: days since the order was last updated
    """

    # Build the path to the CSV file relative to this file's location
    data_path = Path(__file__).parent.parent / "data" / "mock_orders.csv"

    # Load the CSV into a pandas DataFrame
    df = pd.read_csv(data_path)

    # Convert date columns from plain text strings into real Python dates
    date_columns = ["created_date", "due_date", "last_updated"]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])

    # Get today's date (time set to midnight for clean day calculations)
    today = pd.Timestamp.today().normalize()

    # Calculate days until due — negative number means the order is overdue
    df["days_until_due"] = (df["due_date"] - today).dt.days

    # Calculate how many days since the order was last updated
    df["days_since_update"] = (today - df["last_updated"]).dt.days

    # Fill any empty delay_reason or notes cells with an empty string
    df["delay_reason"] = df["delay_reason"].fillna("")
    df["notes"] = df["notes"].fillna("")

    return df