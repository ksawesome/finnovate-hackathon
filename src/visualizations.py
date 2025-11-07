"""Visualization module using Plotly."""

import pandas as pd
import plotly.express as px


def create_dashboard_charts(df: pd.DataFrame) -> list:
    """
    Create dashboard charts for trial balance.

    Args:
        df: DataFrame with data.

    Returns:
        list: List of Plotly figures.
    """
    fig1 = px.bar(df, x='account', y='balance')
    return [fig1]


def plot_insights(df: pd.DataFrame):
    """
    Plot insights from analytics.

    Args:
        df: DataFrame.
    """
    # Placeholder
    pass