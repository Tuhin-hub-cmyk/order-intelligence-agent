import pandas as pd
from pathlib import Path


# Minimum columns needed for the app to function
REQUIRED_COLUMNS = {"status"}

# Columns the app uses — all optional except status
EXPECTED_COLUMNS = {
    "order_id", "customer_name", "order_type", "status",
    "priority", "created_date", "due_date", "assigned_to",
    "product", "value_aud", "last_updated", "delay_reason", "notes"
}


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise column names to lowercase with underscores.
    Handles variations like 'Order ID', 'orderid', 'ORDER_ID' etc.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\-]+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df


def validate_columns(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Check if the DataFrame has the minimum required columns.

    Returns:
        (is_valid: bool, message: str)
    """
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return False, (
            f"Missing required column(s): {', '.join(missing)}. "
            f"Please download the template and match the format."
        )
    return True, "OK"


def load_orders(uploaded_file=None) -> pd.DataFrame:
    """
    Load and clean order data from either an uploaded CSV
    or the default mock data file.

    Args:
        uploaded_file: Streamlit UploadedFile object (optional)

    Returns:
        Clean DataFrame with parsed dates and calculated fields

    Raises:
        ValueError: if the uploaded file is missing required columns
    """

    # Load from uploaded file or fall back to mock data
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            raise ValueError(
                "Could not read the file. "
                "Please make sure it is a valid CSV file."
            )

        # Normalise column names
        df = normalise_columns(df)

        # Validate minimum required columns
        is_valid, message = validate_columns(df)
        if not is_valid:
            raise ValueError(message)

    else:
        data_path = (
            Path(__file__).parent.parent / "data" / "mock_orders.csv"
        )
        df = pd.read_csv(data_path)
        df = normalise_columns(df)

    # Add any missing optional columns as empty/zero defaults
    defaults = {
        "order_id":      lambda i: f"ROW-{i+1:03d}",
        "customer_name": "Unknown",
        "order_type":    "Unknown",
        "priority":      "Medium",
        "assigned_to":   "Unassigned",
        "product":       "—",
        "value_aud":     0,
        "delay_reason":  "",
        "notes":         "",
    }
    for col, default in defaults.items():
        if col not in df.columns:
            if callable(default):
                df[col] = [default(i) for i in range(len(df))]
            else:
                df[col] = default

    # Parse date columns — handle missing columns gracefully
    for col in ["created_date", "due_date", "last_updated"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Today's date
    today = pd.Timestamp.today().normalize()

    # Days until due — negative means overdue
    if "due_date" in df.columns:
        df["days_until_due"] = (df["due_date"] - today).dt.days.fillna(0).astype(int)
    else:
        df["days_until_due"] = 0

    # Days since last update
    if "last_updated" in df.columns:
        df["days_since_update"] = (today - df["last_updated"]).dt.days.fillna(0).astype(int)
    else:
        df["days_since_update"] = 0

    # Clean text columns
    for col in ["delay_reason", "notes", "status", "assigned_to"]:
        df[col] = df[col].fillna("").astype(str)

    # Ensure value_aud is numeric
    df["value_aud"] = pd.to_numeric(df["value_aud"], errors="coerce").fillna(0)

    return df