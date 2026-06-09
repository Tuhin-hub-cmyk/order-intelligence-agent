import pandas as pd


# Priority ranking for sorting (lower number = more urgent)
FLAG_PRIORITY = {
    "OVERDUE": 1,
    "BLOCKED": 2,
    "AT_RISK": 3,
    "STALE": 4,
    "ON_TRACK": 5,
    "COMPLETED": 6,
}


def assign_flag(row: pd.Series) -> str:
    """
    Assign a priority flag to a single order.
    Conditions are checked in priority order — first match wins.
    """

    # Completed orders need no action
    if row["status"] == "Completed":
        return "COMPLETED"

    # Overdue: due date has passed and order is not completed
    if row["days_until_due"] < 0:
        return "OVERDUE"

    # Blocked or Escalated: something is actively stopping this order
    if row["status"] in ["Blocked", "Escalated"]:
        return "BLOCKED"

    # At Risk: status is At Risk, or due within the next 3 days
    if row["status"] == "At Risk" or row["days_until_due"] <= 3:
        return "AT_RISK"

    # Stale: no update in more than 5 days and not completed
    if row["days_since_update"] > 5:
        return "STALE"

    # Everything else is healthy
    return "ON_TRACK"


def analyse_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, list]:
    """
    Run automated analysis on the orders DataFrame.

    Returns:
        df        : original DataFrame with a new 'flag' column added
        summary   : dict with order counts and total value at risk
        priorities: list of top 5 most urgent orders as dicts
    """

    # Work on a copy so we never modify the original data
    df = df.copy()

    # Apply the flag function to every row
    df["flag"] = df.apply(assign_flag, axis=1)

    # Calculate value at risk — safely handle missing value_aud column
    at_risk_df = df[df["flag"].isin(["OVERDUE", "BLOCKED", "AT_RISK"])]
    total_value_at_risk = (
        int(at_risk_df["value_aud"].sum())
        if "value_aud" in df.columns
        else 0
    )

    # Build the summary statistics
    summary = {
        "total_orders":           len(df),
        "overdue_count":          int(len(df[df["flag"] == "OVERDUE"])),
        "blocked_count":          int(len(df[df["flag"] == "BLOCKED"])),
        "at_risk_count":          int(len(df[df["flag"] == "AT_RISK"])),
        "stale_count":            int(len(df[df["flag"] == "STALE"])),
        "on_track_count":         int(len(df[df["flag"] == "ON_TRACK"])),
        "completed_count":        int(len(df[df["flag"] == "COMPLETED"])),
        "total_value_at_risk_aud": total_value_at_risk,
    }

    # Build the top 5 priorities list
    # Sort by flag urgency first, then by most overdue first
    df["flag_rank"] = df["flag"].map(FLAG_PRIORITY)

    # Only include columns that actually exist in the DataFrame
    priority_cols = [
        col for col in [
            "order_id",
            "customer_name",
            "status",
            "flag",
            "days_until_due",
            "assigned_to",
            "delay_reason",
        ]
        if col in df.columns
    ]

    priorities = (
        df[df["flag"] != "COMPLETED"]
        .sort_values(["flag_rank", "days_until_due"])
        .head(5)[priority_cols]
        .to_dict("records")
    )

    # Remove the helper ranking column before returning
    df = df.drop(columns=["flag_rank"])

    return df, summary, priorities