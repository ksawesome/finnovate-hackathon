"""
Visualization module using Plotly.

Comprehensive set of 13+ visualization functions for financial dashboards:
1. Variance Waterfall Chart
2. Hygiene Gauge
3. Review Status Sunburst
4. SLA Timeline Gantt
5. Variance Heatmap
6. Department Comparison Radar
7. Trend Line Chart
8. Category Breakdown Pie
9. Reviewer Workload Bar
10. Anomaly Scatter
11. Export to PNG
12. Export to HTML
13. Dashboard Layout Composer
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==============================================
# CHART TYPE 1: VARIANCE WATERFALL CHART
# ==============================================


def create_variance_waterfall_chart(
    variance_data: pd.DataFrame | dict,
    title: str = "Variance Waterfall Analysis",
    show_total: bool = True,
    max_items: int = 15,
) -> go.Figure:
    """
    Create waterfall chart showing period-over-period variances.

    Enhanced with total bar, better formatting, and flexible input types.

    Args:
        variance_data: DataFrame with ['account_name', 'variance'] OR dict with variance details
        title: Chart title
        show_total: Whether to show cumulative total bar
        max_items: Maximum number of items to display

    Returns:
        go.Figure: Plotly waterfall chart
    """
    # Handle dict input (from variance_analysis)
    if isinstance(variance_data, dict):
        if "variance_details" in variance_data:
            details = variance_data["variance_details"]
            df = pd.DataFrame(
                [
                    {
                        "account_name": d.get("category", d.get("account_name", "Unknown")),
                        "variance": d.get("variance_amount", 0),
                    }
                    for d in details
                ]
            )
        else:
            # Simple dict format
            df = pd.DataFrame(list(variance_data.items()), columns=["account_name", "variance"])
    else:
        df = variance_data.copy()

    # Ensure required columns exist
    if "account_name" not in df.columns or "variance" not in df.columns:
        # Try alternate column names
        if "category" in df.columns:
            df["account_name"] = df["category"]
        if "variance_amount" in df.columns:
            df["variance"] = df["variance_amount"]

    # Sort by absolute variance and limit
    df = df.sort_values("variance", key=abs, ascending=False).head(max_items)

    # Build waterfall data
    measures = ["relative"] * len(df)
    x_values = df["account_name"].tolist()
    y_values = df["variance"].tolist()
    text_values = [f"₹{val:,.0f}" for val in y_values]

    # Add total bar if requested
    if show_total:
        measures.append("total")
        x_values.append("Net Variance")
        y_values.append(sum(y_values))
        text_values.append(f"₹{sum(df['variance']):,.0f}")

    # Create waterfall chart
    fig = go.Figure(
        go.Waterfall(
            name="Variance",
            orientation="v",
            measure=measures,
            x=x_values,
            y=y_values,
            connector={"line": {"color": "rgb(63, 63, 63)", "width": 2}},
            increasing={"marker": {"color": "#27ae60", "line": {"color": "#229954", "width": 2}}},
            decreasing={"marker": {"color": "#e74c3c", "line": {"color": "#c0392b", "width": 2}}},
            totals={"marker": {"color": "#3498db", "line": {"color": "#2874a6", "width": 2}}},
            text=text_values,
            textposition="outside",
            textfont={"size": 11, "color": "black"},
            hovertemplate="<b>%{x}</b><br>Variance: ₹%{y:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 18, "color": "#2c3e50"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="GL Account / Category",
        yaxis_title="Variance Amount (₹)",
        showlegend=False,
        height=500,
        template="plotly_white",
        hovermode="x",
        margin=dict(t=80, b=100, l=80, r=40),
    )

    # Add zero reference line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        line_width=1,
        annotation_text="Zero Line",
        annotation_position="right",
    )

    return fig


# ==============================================
# CHART TYPE 2: HYGIENE GAUGE
# ==============================================


def create_hygiene_gauge(
    hygiene_score: float | dict,
    components: dict | None = None,
    title: str = "GL Hygiene Score",
    target: float = 85.0,
) -> go.Figure:
    """
    Create gauge chart showing GL hygiene score.

    Enhanced with dynamic coloring, threshold markers, and component breakdown.

    Args:
        hygiene_score: Overall score (0-100) OR dict with 'overall_score' key
        components: Dict of component scores (optional)
        title: Chart title
        target: Target score for threshold

    Returns:
        go.Figure: Plotly gauge chart with component annotations
    """
    # Handle dict input
    if isinstance(hygiene_score, dict):
        components = (
            hygiene_score.get("component_scores") or hygiene_score.get("components") or components
        )
        hygiene_score = hygiene_score.get("overall_score", 0)

    # Determine color based on score
    if hygiene_score >= 85:
        color = "#27ae60"  # Green
        grade = "Excellent"
    elif hygiene_score >= 70:
        color = "#f39c12"  # Orange
        grade = "Good"
    elif hygiene_score >= 50:
        color = "#e67e22"  # Dark orange
        grade = "Fair"
    else:
        color = "#e74c3c"  # Red
        grade = "Needs Improvement"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=hygiene_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"{title}<br><span style='font-size:0.6em;color:gray'>{grade}</span>",
                "font": {"size": 20},
            },
            delta={
                "reference": target,
                "increasing": {"color": "#27ae60"},
                "decreasing": {"color": "#e74c3c"},
                "suffix": f" (Target: {target})",
            },
            number={"suffix": "/100", "font": {"size": 40}},
            gauge={
                "axis": {
                    "range": [None, 100],
                    "tickwidth": 2,
                    "tickcolor": "#34495e",
                    "tickmode": "linear",
                    "tick0": 0,
                    "dtick": 20,
                },
                "bar": {"color": color, "thickness": 0.75},
                "bgcolor": "white",
                "borderwidth": 3,
                "bordercolor": "#34495e",
                "steps": [
                    {"range": [0, 50], "color": "#fadbd8"},  # Light red
                    {"range": [50, 70], "color": "#fdebd0"},  # Light orange
                    {"range": [70, 85], "color": "#fef9e7"},  # Light yellow
                    {"range": [85, 100], "color": "#d5f4e6"},  # Light green
                ],
                "threshold": {
                    "line": {"color": "#2874a6", "width": 4},
                    "thickness": 0.85,
                    "value": target,
                },
            },
        )
    )

    fig.update_layout(
        height=400,
        margin=dict(l=30, r=30, t=80, b=30),
        paper_bgcolor="white",
        font={"color": "#1b1f23"},
    )

    # Add component breakdown annotation if provided
    if components:
        component_text = "<br>".join(
            [f"{k.replace('_', ' ').title()}: {v:.0f}" for k, v in list(components.items())[:5]]
        )
        fig.add_annotation(
            text=f"<b>Components:</b><br>{component_text}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.15,
            showarrow=False,
            font=dict(size=10, color="#7f8c8d"),
            align="center",
        )

    return fig


# ==============================================
# CHART TYPE 3: REVIEW STATUS SUNBURST
# ==============================================


def create_review_status_sunburst(
    status_data: dict, title: str = "Review Status Breakdown", color_scheme: str = "status"
) -> go.Figure:
    """
    Create sunburst chart showing review status hierarchy.

    Enhanced with flexible data structure and color schemes.

    Args:
        status_data: Dict with status hierarchy (by_criticality, by_category, by_status, etc.)
        title: Chart title
        color_scheme: 'status' for status-based colors, 'gradient' for gradient

    Returns:
        go.Figure: Plotly sunburst chart
    """
    labels = ["Total"]
    parents = [""]
    values = [0]  # Will calculate from children
    colors = []

    # Color mapping for status-based scheme
    status_colors = {
        "reviewed": "#27ae60",
        "approved": "#229954",
        "pending": "#f39c12",
        "in_review": "#3498db",
        "flagged": "#e74c3c",
        "critical": "#c0392b",
        "high": "#e67e22",
        "medium": "#f39c12",
        "low": "#3498db",
    }

    # Build hierarchy from status_data
    total_count = 0

    # Handle different data structures
    if "by_status" in status_data:
        for status, count in status_data["by_status"].items():
            labels.append(status.title())
            parents.append("Total")
            values.append(count)
            colors.append(status_colors.get(status.lower(), "#95a5a6"))
            total_count += count

    elif "by_criticality" in status_data:
        for crit, statuses in status_data["by_criticality"].items():
            crit_total = sum(statuses.values()) if isinstance(statuses, dict) else statuses
            labels.append(crit.title())
            parents.append("Total")
            values.append(crit_total)
            colors.append(status_colors.get(crit.lower(), "#95a5a6"))
            total_count += crit_total

            # Add status breakdown if dict
            if isinstance(statuses, dict):
                for status, count in statuses.items():
                    labels.append(f"{status.title()}")
                    parents.append(crit.title())
                    values.append(count)
                    colors.append(status_colors.get(status.lower(), "#95a5a6"))

    elif "by_department" in status_data:
        for dept, dept_data in status_data["by_department"].items():
            dept_total = sum(dept_data.values()) if isinstance(dept_data, dict) else dept_data
            labels.append(dept)
            parents.append("Total")
            values.append(dept_total)
            colors.append("#3498db")
            total_count += dept_total

            if isinstance(dept_data, dict):
                for status, count in dept_data.items():
                    labels.append(f"{dept}-{status}")
                    parents.append(dept)
                    values.append(count)
                    colors.append(status_colors.get(status.lower(), "#95a5a6"))

    else:
        # Flat structure - treat as simple categories
        for key, value in status_data.items():
            labels.append(str(key).title())
            parents.append("Total")
            values.append(value)
            colors.append(status_colors.get(str(key).lower(), "#95a5a6"))
            total_count += value

    # Set total
    values[0] = total_count

    # Create sunburst
    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors if color_scheme == "status" else None,
                colorscale="RdYlGn_r" if color_scheme == "gradient" else None,
                line=dict(color="white", width=2),
            ),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percentRoot:.1%} of Total<extra></extra>",
            textinfo="label+percent parent",
            insidetextorientation="radial",
        )
    )

    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 18, "color": "#2c3e50"},
            "x": 0.5,
            "xanchor": "center",
        },
        height=500,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="white",
    )

    return fig


# ==============================================
# CHART TYPE 4: SLA TIMELINE GANTT
# ==============================================


def create_sla_timeline_gantt(assignments: list[dict], title: str = "SLA Timeline") -> go.Figure:
    """
    Create Gantt chart showing SLA timelines for account reviews.

    Args:
        assignments: List of assignment dicts with account_code, assigned_date, deadline, status
        title: Chart title

    Returns:
        go.Figure: Plotly Gantt chart
    """
    if not assignments:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No assignment data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df = pd.DataFrame(assignments)

    # Status color mapping
    color_map = {
        "Reviewed": "#2ecc71",
        "Approved": "#27ae60",
        "Pending": "#f39c12",
        "Flagged": "#e74c3c",
        "Overdue": "#c0392b",
    }

    fig = go.Figure()

    for idx, row in df.iterrows():
        fig.add_trace(
            go.Bar(
                name=row.get("account_code", f"Account {idx}"),
                x=[row.get("duration", 5)],  # Duration in days
                y=[row.get("account_code", f"Account {idx}")],
                orientation="h",
                marker=dict(color=color_map.get(row.get("status", "Pending"), "#95a5a6")),
                hovertext=f"Account: {row.get('account_code')}<br>Status: {row.get('status')}<br>Deadline: {row.get('deadline')}",
                hoverinfo="text",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Days",
        yaxis_title="GL Accounts",
        showlegend=False,
        height=max(400, len(assignments) * 30),
        barmode="overlay",
        template="plotly_white",
    )

    return fig


def create_variance_heatmap(
    variance_data: pd.DataFrame,  # Rows=accounts, Cols=periods
    title: str = "GL Account Variance Heatmap",
) -> go.Figure:
    """
    Create heatmap showing variance patterns across accounts and periods.

    Args:
        variance_data: DataFrame with accounts as rows, periods as columns
        title: Chart title

    Returns:
        go.Figure: Plotly heatmap
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=variance_data.values,
            x=variance_data.columns.tolist(),
            y=variance_data.index.tolist(),
            colorscale=[
                [0, "#e74c3c"],  # Red for negative
                [0.5, "#f8f9fa"],  # White for neutral
                [1, "#2ecc71"],  # Green for positive
            ],
            zmid=0,
            text=variance_data.values,
            texttemplate="%{text:.0f}",
            textfont={"size": 10},
            colorbar=dict(title="Variance (%)"),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="GL Account",
        height=max(400, len(variance_data) * 20),
        template="plotly_white",
    )

    return fig


def create_department_comparison_radar(
    dept_metrics: dict, title: str = "Department Performance Comparison"
) -> go.Figure:
    """
    Create radar chart comparing departments on multiple metrics.

    Args:
        dept_metrics: Dict with department as key, metrics dict as value
        title: Chart title

    Returns:
        go.Figure: Plotly radar chart
    """
    fig = go.Figure()

    # Metrics to compare
    metrics = ["completion_rate", "hygiene_score", "sla_compliance", "doc_completeness"]

    for dept, values in dept_metrics.items():
        fig.add_trace(
            go.Scatterpolar(
                r=[values.get(m, 0) for m in metrics], theta=metrics, fill="toself", name=dept
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=title,
        height=500,
    )

    return fig


def create_trend_line_chart(
    trend_data: dict,  # Keys=metric_name, Values=list of values
    periods: list[str],
    title: str = "Trend Analysis",
) -> go.Figure:
    """
    Create multi-line trend chart showing metrics over time.

    Args:
        trend_data: Dict with metric names as keys, value lists as values
        periods: List of period labels
        title: Chart title

    Returns:
        go.Figure: Plotly line chart
    """
    fig = go.Figure()

    for metric, values in trend_data.items():
        fig.add_trace(
            go.Scatter(
                x=periods,
                y=values,
                mode="lines+markers",
                name=metric,
                line=dict(width=3),
                marker=dict(size=8),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title="Value",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_category_breakdown_pie(
    category_data: dict, title: str = "Balance by Category"
) -> go.Figure:
    """
    Create pie chart showing balance breakdown by category.

    Args:
        category_data: Dict with category as key, balance as value
        title: Chart title

    Returns:
        go.Figure: Plotly pie chart
    """
    labels = list(category_data.keys())
    values = list(category_data.values())

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
                marker=dict(colors=px.colors.qualitative.Set3, line=dict(color="white", width=2)),
            )
        ]
    )

    fig.update_layout(title=title, height=400, showlegend=True)

    return fig


def create_reviewer_workload_bar(
    reviewer_stats: list[dict], title: str = "Reviewer Workload"
) -> go.Figure:
    """
    Create horizontal bar chart showing reviewer workload distribution.

    Args:
        reviewer_stats: List of dicts with 'reviewer', 'assigned', 'completed', 'pending'
        title: Chart title

    Returns:
        go.Figure: Plotly bar chart
    """
    df = pd.DataFrame(reviewer_stats)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Completed",
            y=df["reviewer"],
            x=df["completed"],
            orientation="h",
            marker=dict(color="#2ecc71"),
        )
    )

    fig.add_trace(
        go.Bar(
            name="Pending",
            y=df["reviewer"],
            x=df["pending"],
            orientation="h",
            marker=dict(color="#f39c12"),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Number of Accounts",
        yaxis_title="Reviewer",
        barmode="stack",
        height=max(300, len(reviewer_stats) * 50),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def create_anomaly_scatter(anomaly_data: list[dict], title: str = "Anomaly Detection") -> go.Figure:
    """
    Create scatter plot showing anomalous accounts.

    Args:
        anomaly_data: List of dicts with 'account_code', 'balance', 'z_score', 'category'
        title: Chart title

    Returns:
        go.Figure: Plotly scatter chart
    """
    if not anomaly_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No anomalies detected",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16),
        )
        return fig

    df = pd.DataFrame(anomaly_data)

    fig = px.scatter(
        df,
        x="balance",
        y="z_score",
        color="category",
        size="z_score",
        hover_data=["account_code", "account_name"],
        title=title,
        labels={"balance": "Account Balance (₹)", "z_score": "Anomaly Score (Z-score)"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # Add threshold line
    fig.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="Anomaly Threshold")

    fig.update_layout(height=500, template="plotly_white")

    return fig


# ==============================================
# CHART TYPE 11: EXPORT TO PNG
# ==============================================


def export_chart_to_png(
    fig: go.Figure, output_path: str, width: int = 1200, height: int = 800, scale: float = 2.0
) -> str:
    """
    Export Plotly chart to static PNG image.

    Enhanced with scale parameter for high-DPI displays.

    Args:
        fig: Plotly figure
        output_path: Output file path
        width: Image width in pixels
        height: Image height in pixels
        scale: Scale factor for resolution (2.0 = retina display)

    Returns:
        str: Path to exported file
    """
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Export to PNG with kaleido (preferred) or orca
        fig.write_image(output_path, width=width, height=height, scale=scale, format="png")
        return output_path
    except Exception as e:
        # Fallback: save as HTML if PNG export fails
        html_path = output_path.replace(".png", ".html")
        fig.write_html(html_path)
        print(f"PNG export failed: {e}. Saved as HTML instead: {html_path}")
        return html_path


# ==============================================
# CHART TYPE 12: EXPORT TO HTML
# ==============================================


def export_chart_to_html(
    fig: go.Figure,
    output_path: str,
    include_plotlyjs: bool | str = "cdn",
    config: dict | None = None,
) -> str:
    """
    Export interactive Plotly chart to standalone HTML.

    Enhanced with config options and plotly.js handling.

    Args:
        fig: Plotly figure
        output_path: Output file path
        include_plotlyjs: 'cdn' (default), True (inline), or False (external)
        config: Plotly config dict (e.g., {'displayModeBar': False})

    Returns:
        str: Path to exported file
    """
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Default config for better interactivity
    if config is None:
        config = {
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "chart",
                "height": 800,
                "width": 1200,
                "scale": 2,
            },
        }

    # Export to HTML
    fig.write_html(output_path, include_plotlyjs=include_plotlyjs, config=config, auto_open=False)

    return output_path


# ==============================================
# CHART TYPE 13: DASHBOARD LAYOUT COMPOSER
# ==============================================


def create_dashboard_layout(
    charts: list[go.Figure],
    layout: str = "grid",
    cols: int = 2,
    titles: list[str] | None = None,
    shared_xaxes: bool = False,
    shared_yaxes: bool = False,
    vertical_spacing: float = 0.1,
    horizontal_spacing: float = 0.1,
) -> go.Figure:
    """
    Combine multiple charts into a single dashboard layout.

    Enhanced with titles, spacing control, and axis sharing options.

    Args:
        charts: List of Plotly figures
        layout: Layout type ('grid', 'vertical', 'horizontal')
        cols: Number of columns for grid layout
        titles: List of subplot titles (optional)
        shared_xaxes: Share x-axes across subplots
        shared_yaxes: Share y-axes across subplots
        vertical_spacing: Vertical space between subplots (0-1)
        horizontal_spacing: Horizontal space between subplots (0-1)

    Returns:
        go.Figure: Combined dashboard figure
    """
    n_charts = len(charts)

    if n_charts == 0:
        return go.Figure()

    # Generate default titles if not provided
    if titles is None:
        titles = [f"Chart {i+1}" for i in range(n_charts)]

    # Calculate layout dimensions
    if layout == "grid":
        rows = (n_charts + cols - 1) // cols
        subplot_cols = cols
        subplot_rows = rows
    elif layout == "vertical":
        subplot_rows = n_charts
        subplot_cols = 1
    elif layout == "horizontal":
        subplot_rows = 1
        subplot_cols = n_charts
    else:
        # Default to grid
        rows = (n_charts + cols - 1) // cols
        subplot_cols = cols
        subplot_rows = rows

    # Create subplots
    fig = make_subplots(
        rows=subplot_rows,
        cols=subplot_cols,
        subplot_titles=titles[:n_charts],
        shared_xaxes=shared_xaxes,
        shared_yaxes=shared_yaxes,
        vertical_spacing=vertical_spacing,
        horizontal_spacing=horizontal_spacing,
        specs=[[{"type": "xy"} for _ in range(subplot_cols)] for _ in range(subplot_rows)],
    )

    # Add traces from each chart
    for idx, chart in enumerate(charts):
        if layout == "grid":
            row = idx // cols + 1
            col = idx % cols + 1
        elif layout == "vertical":
            row = idx + 1
            col = 1
        elif layout == "horizontal":
            row = 1
            col = idx + 1
        else:
            row = idx // cols + 1
            col = idx % cols + 1

        # Add all traces from the chart
        for trace in chart.data:
            fig.add_trace(trace, row=row, col=col)

        # Copy axis titles if they exist
        if chart.layout.xaxis.title.text:
            fig.update_xaxes(title_text=chart.layout.xaxis.title.text, row=row, col=col)
        if chart.layout.yaxis.title.text:
            fig.update_yaxes(title_text=chart.layout.yaxis.title.text, row=row, col=col)

    # Update overall layout
    fig.update_layout(
        height=400 * subplot_rows,
        showlegend=True,
        template="plotly_white",
        title={
            "text": "Dashboard Overview",
            "font": {"size": 24, "color": "#2c3e50"},
            "x": 0.5,
            "xanchor": "center",
        },
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(t=100, b=100, l=80, r=80),
    )

    return fig


# ==============================================
# UTILITY FUNCTIONS
# ==============================================


def apply_theme(fig: go.Figure, theme: str = "light") -> go.Figure:
    """
    Apply consistent theme to Plotly figure.

    Args:
        fig: Plotly figure
        theme: 'light', 'dark', or 'presentation'

    Returns:
        go.Figure: Themed figure
    """
    themes = {
        "light": {
            "template": "plotly_white",
            "paper_bgcolor": "white",
            "plot_bgcolor": "#f8f9fa",
            "font_color": "#2c3e50",
        },
        "dark": {
            "template": "plotly_dark",
            "paper_bgcolor": "#1e1e1e",
            "plot_bgcolor": "#2d2d2d",
            "font_color": "#ecf0f1",
        },
        "presentation": {
            "template": "presentation",
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "font_color": "#2c3e50",
        },
    }

    theme_config = themes.get(theme, themes["light"])

    fig.update_layout(
        template=theme_config["template"],
        paper_bgcolor=theme_config["paper_bgcolor"],
        plot_bgcolor=theme_config["plot_bgcolor"],
        font={"color": theme_config["font_color"]},
    )

    return fig


def add_watermark(
    fig: go.Figure, text: str = "Project Aura", position: str = "bottom-right"
) -> go.Figure:
    """
    Add watermark to Plotly figure.

    Args:
        fig: Plotly figure
        text: Watermark text
        position: 'bottom-right', 'bottom-left', 'top-right', 'top-left', 'center'

    Returns:
        go.Figure: Figure with watermark
    """
    positions = {
        "bottom-right": {"x": 0.95, "y": 0.05, "xanchor": "right", "yanchor": "bottom"},
        "bottom-left": {"x": 0.05, "y": 0.05, "xanchor": "left", "yanchor": "bottom"},
        "top-right": {"x": 0.95, "y": 0.95, "xanchor": "right", "yanchor": "top"},
        "top-left": {"x": 0.05, "y": 0.95, "xanchor": "left", "yanchor": "top"},
        "center": {"x": 0.5, "y": 0.5, "xanchor": "center", "yanchor": "middle"},
    }

    pos = positions.get(position, positions["bottom-right"])

    fig.add_annotation(
        text=text,
        xref="paper",
        yref="paper",
        x=pos["x"],
        y=pos["y"],
        xanchor=pos["xanchor"],
        yanchor=pos["yanchor"],
        showarrow=False,
        font=dict(size=10, color="rgba(150, 150, 150, 0.5)"),
        opacity=0.3,
    )

    return fig
