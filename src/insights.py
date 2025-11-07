"""Insights generation module."""

import pandas as pd


def generate_insights(df: pd.DataFrame) -> list:
    """
    Generate key insights from data.

    Args:
        df: Analyzed DataFrame.

    Returns:
        list: List of insight strings.
    """
    insights = []
    # Placeholder logic
    total_balance = df.get("balance", pd.Series()).sum()
    insights.append(f"Total balance: {total_balance}")
    return insights


def drill_down_analysis(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Perform drill-down analysis.

    Args:
        df: DataFrame.
        filters: Dict of filters.

    Returns:
        pd.DataFrame: Filtered data.
    """
    for col, val in filters.items():
        df = df[df[col] == val]
    return df
