import pandas as pd
from pathlib import Path


def load_orders(uploaded_file=None) -> pd.DataFrame:
    """
    Load and clean order data from either an uploaded CSV
    or the default mock data file.

    Args:
        uploaded_file: Streamlit UploadedFile object (optional)

    Returns:
        Clean DataFrame with parsed dates and calculated fields
    """

    # Load from uploaded file or fall back to mock data
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        data_path = (
            Path(__file__).parent.parent / "data" / "mock_orders.csv"
        )
        df = pd.read_csv(data_path)

    # Parse date columns — handle missing columns gracefully
    date_columns = ["created_date", "due_date", "last_updated"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Today's date with time set to midnight
    today = pd.Timestamp.today().normalize()

    # Days until due — negative means overdue
    if "due_date" in df.columns:
        df["days_until_due"] = (df["due_date"] - today).dt.days
    else:
        df["days_until_due"] = 0

    # Days since the order was last updated
    if "last_updated" in df.columns:
        df["days_since_update"] = (today - df["last_updated"]).dt.days
    else:
        df["days_since_update"] = 0

    # Fill empty text columns with empty string
    for col in ["delay_reason", "notes", "status", "assigned_to"]:
        if col in df.columns:
            df[col] = df[col].fillna("")
        else:
            df[col] = ""

    return df