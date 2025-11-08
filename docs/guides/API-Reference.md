# API Reference - Project Aura

**Version:** 1.0.0
**Last Updated:** 2024
**Module Coverage:** analytics, insights, visualizations

---

## Table of Contents

1. [Analytics Module](#analytics-module)
2. [Insights Module](#insights-module)
3. [Visualizations Module](#visualizations-module)
4. [Common Patterns](#common-patterns)
5. [Error Handling](#error-handling)

---

## Analytics Module

Located in: `src/analytics.py`

### `perform_analytics(entity: str, period: str) -> dict`

Perform comprehensive analytics on GL accounts for a given entity and period.

**Parameters:**
- `entity` (str): Entity code (e.g., "Entity001")
- `period` (str): Period in YYYY-MM format (e.g., "2024-03")

**Returns:**
- `dict`: Analytics results containing:
  - `by_category` (dict): Balance grouped by account category
  - `by_department` (dict): Balance grouped by department
  - `total_balance` (float): Total balance across all accounts
  - `account_count` (int): Number of accounts analyzed
  - `error` (str, optional): Error message if operation fails

**Example:**
```python
from src.analytics import perform_analytics

result = perform_analytics("Entity001", "2024-03")
print(f"Total Balance: ₹{result['total_balance']:,.2f}")
print(f"Categories: {list(result['by_category'].keys())}")
```

**Performance:** < 500ms for 501 accounts

---

### `calculate_variance_analysis(entity: str, current_period: str, previous_period: str) -> dict`

Calculate period-over-period variance for GL accounts.

**Parameters:**
- `entity` (str): Entity code
- `current_period` (str): Current period (YYYY-MM)
- `previous_period` (str): Previous period (YYYY-MM)

**Returns:**
- `dict`: Variance analysis containing:
  - `accounts_analyzed` (int): Number of accounts compared
  - `total_variance` (float): Sum of all variances
  - `significant_variances` (list[dict]): Accounts with >10% or >₹50k variance
    - `account_code` (str)
    - `account_name` (str)
    - `current_balance` (float)
    - `previous_balance` (float)
    - `variance` (float)
    - `variance_pct` (float)
  - `significant_count` (int): Count of significant variances
  - `error` (str, optional)

**Example:**
```python
variance = calculate_variance_analysis("Entity001", "2024-03", "2024-02")
for item in variance['significant_variances']:
    print(f"{item['account_name']}: {item['variance_pct']:.1f}% change")
```

---

### `calculate_review_status_summary(entity: str, period: str) -> dict`

Calculate review status summary grouped by various dimensions.

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)

**Returns:**
- `dict`: Status summary containing:
  - `by_criticality` (dict): Status counts grouped by criticality level
  - `by_category` (dict): Status counts grouped by account category
  - `by_department` (dict): Status counts grouped by department
  - `overall_completion_rate` (float): Percentage of reviewed accounts
  - `error` (str, optional)

**Example:**
```python
status = calculate_review_status_summary("Entity001", "2024-03")
print(f"Completion Rate: {status['overall_completion_rate']:.1f}%")
print(f"High Criticality: {status['by_criticality']['High']}")
```

---

### `calculate_gl_hygiene_score(entity: str, period: str) -> dict`

Calculate GL hygiene score based on 4 components (100-point scale).

**Components:**
1. Review Completion (30 points): % of accounts reviewed
2. Documentation Completeness (25 points): % with supporting docs
3. SLA Compliance (25 points): % reviewed within deadline
4. Variance Resolution (20 points): % of flagged variances resolved

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)

**Returns:**
- `dict`: Hygiene score containing:
  - `overall_score` (float): 0-100 score
  - `grade` (str): Letter grade (A+, A, B+, B, C+, C, D, F)
  - `components` (dict): Individual component scores
    - `review_completion_score` (float)
    - `documentation_score` (float)
    - `sla_score` (float)
    - `variance_resolution_score` (float)
  - `error` (str, optional)

**Example:**
```python
hygiene = calculate_gl_hygiene_score("Entity001", "2024-03")
print(f"Hygiene Score: {hygiene['overall_score']:.1f}/100 ({hygiene['grade']})")
```

---

### `get_pending_items_report(entity: str, period: str) -> dict`

Get report of all pending reviews, missing docs, and flagged items.

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)

**Returns:**
- `dict`: Pending items report containing:
  - `pending_reviews_count` (int)
  - `missing_docs_count` (int)
  - `flagged_items_count` (int)
  - `pending_reviews` (list[dict]): Accounts with pending reviews
  - `missing_docs` (list[dict]): Accounts missing documentation
  - `flagged_items` (list[dict]): Accounts flagged for attention
  - `error` (str, optional)

**Example:**
```python
pending = get_pending_items_report("Entity001", "2024-03")
print(f"Pending Reviews: {pending['pending_reviews_count']}")
for item in pending['pending_reviews'][:5]:
    print(f"  {item['account_code']}: {item['criticality']} priority")
```

---

### `identify_anomalies_ml(entity: str, period: str, threshold: float = 2.0) -> dict`

Identify anomalous account balances using Z-score statistical analysis.

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)
- `threshold` (float, optional): Z-score threshold (default: 2.0)
  - 2.0 = ~95% confidence (moderate sensitivity)
  - 2.5 = ~98% confidence
  - 3.0 = ~99.7% confidence (low false positives)

**Returns:**
- `dict`: Anomaly detection results containing:
  - `anomaly_count` (int): Total anomalies detected
  - `critical_count` (int): Anomalies with z-score > 3.0
  - `high_count` (int): Anomalies with z-score 2.5-3.0
  - `medium_count` (int): Anomalies with z-score 2.0-2.5
  - `categories_analyzed` (int): Number of categories analyzed
  - `anomalies` (list[dict]): Anomalous accounts
    - `account_code` (str)
    - `account_name` (str)
    - `category` (str)
    - `balance` (float)
    - `z_score` (float)
    - `severity` (str): critical/high/medium
  - `error` (str, optional)

**Example:**
```python
anomalies = identify_anomalies_ml("Entity001", "2024-03", threshold=2.5)
print(f"Anomalies Found: {anomalies['anomaly_count']}")
for anom in anomalies['anomalies']:
    print(f"  {anom['account_name']}: Z-score {anom['z_score']:.2f} ({anom['severity']})")
```

**Note:** Requires `scipy` package. Install with: `conda install scipy`

---

### `export_analytics_to_csv(analytics_dict: dict, output_path: str) -> str`

Export analytics results to CSV file.

**Parameters:**
- `analytics_dict` (dict): Analytics dictionary from any analytics function
- `output_path` (str): Output file path (e.g., "data/reports/analytics.csv")

**Returns:**
- `str`: Path to exported file

---

### `export_analytics_to_excel(analytics_dict: dict, output_path: str) -> str`

Export analytics results to multi-sheet Excel file.

**Parameters:**
- `analytics_dict` (dict): Analytics dictionary
- `output_path` (str): Output file path (e.g., "data/reports/analytics.xlsx")

**Returns:**
- `str`: Path to exported file

**Features:**
- Multiple sheets for summary and details
- Formatted headers
- Auto-adjusted column widths

---

## Insights Module

Located in: `src/insights.py`

### `generate_proactive_insights(entity: str, period: str) -> dict`

Generate proactive insights with priority classification and recommendations.

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)

**Returns:**
- `dict`: Insights containing:
  - `insights` (list[dict]): List of insights (minimum 5)
    - `type` (str): quality_alert | anomaly_detected | critical_items | documentation_gap | info
    - `priority` (str): critical | high | medium | info
    - `message` (str): Human-readable insight message
    - `recommendation` (str): Actionable recommendation
  - `error` (str, optional)

**Priority Levels:**
- **critical**: Immediate action required (hygiene < 60, critical anomalies)
- **high**: Address within 24h (hygiene 60-70, pending high-priority items)
- **medium**: Address within 48h (hygiene 70-80, moderate issues)
- **info**: Informational (hygiene > 80, status updates)

**Example:**
```python
insights = generate_proactive_insights("Entity001", "2024-03")
for insight in insights['insights']:
    icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'info': '🔵'}[insight['priority']]
    print(f"{icon} {insight['message']}")
    print(f"   → {insight['recommendation']}")
```

---

### `generate_executive_summary(entity: str, period: str) -> dict`

Generate executive summary for leadership with overall status assessment.

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)

**Returns:**
- `dict`: Executive summary containing:
  - `overall_status` (str): Excellent | Good | Fair | Needs Attention
  - `key_metrics` (dict):
    - `total_accounts` (int)
    - `total_balance` (float)
    - `hygiene_score` (float)
    - `completion_rate` (float)
  - `highlights` (list[str]): Positive indicators (3-5 items)
  - `concerns` (list[str]): Areas needing attention (0-5 items)
  - `recommendations` (list[str]): Actionable recommendations (3-5 items)
  - `error` (str, optional)

**Status Thresholds:**
- **Excellent**: Hygiene ≥ 85 AND Completion ≥ 90%
- **Good**: Hygiene ≥ 75 AND Completion ≥ 75%
- **Fair**: Hygiene ≥ 60 AND Completion ≥ 60%
- **Needs Attention**: Below Fair thresholds

**Example:**
```python
summary = generate_executive_summary("Entity001", "2024-03")
print(f"Status: {summary['overall_status']}")
print(f"Hygiene Score: {summary['key_metrics']['hygiene_score']:.1f}")
print("\nHighlights:")
for h in summary['highlights']:
    print(f"  ✓ {h}")
```

---

### `generate_drill_down_report(entity: str, period: str, dimension: str, value: str) -> dict`

Generate detailed drill-down report filtered by specific dimension.

**Parameters:**
- `entity` (str): Entity code
- `period` (str): Period (YYYY-MM)
- `dimension` (str): Filter dimension (category | department | criticality | review_status)
- `value` (str): Dimension value (e.g., "Assets", "Finance", "High", "Pending")

**Returns:**
- `dict`: Drill-down report containing:
  - `summary_metrics` (dict):
    - `total_accounts` (int)
    - `total_balance` (float)
    - `avg_balance` (float)
    - `completion_rate` (float)
  - `status_distribution` (dict): Count by review status
  - `top_accounts` (list[dict]): Top 10 accounts by balance
  - `error` (str, optional)

**Example:**
```python
report = generate_drill_down_report("Entity001", "2024-03", "category", "Assets")
print(f"Assets: {report['summary_metrics']['total_accounts']} accounts")
print(f"Total Balance: ₹{report['summary_metrics']['total_balance']:,.2f}")
```

---

### `compare_multi_period(entity: str, periods: list[str]) -> dict`

Compare metrics across multiple periods to identify trends.

**Parameters:**
- `entity` (str): Entity code
- `periods` (list[str]): List of periods in YYYY-MM format (chronological order)

**Returns:**
- `dict`: Multi-period comparison containing:
  - `period_summaries` (list[dict]): Summary for each period
    - `period` (str)
    - `total_balance` (float)
    - `hygiene_score` (float)
    - `completion_rate` (float)
    - `account_count` (int)
  - `trends` (dict): Trend analysis
    - `total_balance` (dict):
      - `direction` (str): increasing | decreasing | stable
      - `change_amount` (float)
      - `change_pct` (float)
    - (similar for hygiene_score, completion_rate)
  - `error` (str, optional)

**Trend Thresholds:**
- **increasing**: Change ≥ +5%
- **decreasing**: Change ≤ -5%
- **stable**: Change between -5% and +5%

**Example:**
```python
comparison = compare_multi_period("Entity001", ["2024-01", "2024-02", "2024-03"])
for trend_name, trend_data in comparison['trends'].items():
    print(f"{trend_name}: {trend_data['direction']} ({trend_data['change_pct']:.1f}%)")
```

---

## Visualizations Module

Located in: `src/visualizations.py`

All visualization functions return `plotly.graph_objects.Figure` objects suitable for rendering in Streamlit or exporting to HTML/PNG.

### `create_variance_waterfall_chart(variance_df: pd.DataFrame, title: str = "Variance Waterfall Analysis") -> go.Figure`

Create waterfall chart showing variances (top 15 accounts by absolute variance).

**Parameters:**
- `variance_df` (pd.DataFrame): DataFrame with columns `account_name`, `variance`
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

**Chart Features:**
- Green bars for positive variance
- Red bars for negative variance
- Value labels on bars
- Top 15 accounts only

---

### `create_hygiene_gauge(hygiene_score: float, components: dict, title: str = "GL Hygiene Score") -> go.Figure`

Create gauge chart showing hygiene score (0-100 scale).

**Parameters:**
- `hygiene_score` (float): Overall score (0-100)
- `components` (dict): Component scores dictionary
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

**Gauge Zones:**
- Green (80-100): Excellent
- Orange (60-80): Fair
- Red (0-60): Needs Attention

---

### `create_review_status_sunburst(status_data: dict, title: str = "Review Status Breakdown") -> go.Figure`

Create hierarchical sunburst chart for status breakdown.

**Parameters:**
- `status_data` (dict): Dict with `by_criticality` and/or `by_category` keys
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

**Hierarchy:** Total → Criticality → Status

---

### `create_category_breakdown_pie(category_data: dict, title: str = "Balance by Category") -> go.Figure`

Create pie chart showing balance distribution by category.

**Parameters:**
- `category_data` (dict): Category as key, balance as value
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

**Features:**
- Percentage and absolute values
- Hover tooltips with formatted amounts
- Professional color scheme

---

### `create_reviewer_workload_bar(reviewer_stats: list[dict], title: str = "Reviewer Workload") -> go.Figure`

Create horizontal stacked bar chart for reviewer workload.

**Parameters:**
- `reviewer_stats` (list[dict]): List of dicts with `reviewer`, `completed`, `pending` keys
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

**Features:**
- Stacked bars (completed + pending)
- Color coding (green for completed, orange for pending)

---

### `create_anomaly_scatter(anomaly_data: list[dict], title: str = "Anomaly Detection") -> go.Figure`

Create scatter plot showing anomalous accounts.

**Parameters:**
- `anomaly_data` (list[dict]): List of anomalies with `account_code`, `balance`, `z_score`, `category` keys
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

**Features:**
- Color by category
- Size by z-score
- Threshold line at z=2.0
- Hover info with account details

---

### `create_trend_line_chart(trend_data: dict, periods: list[str], title: str = "Trend Analysis") -> go.Figure`

Create multi-line trend chart.

**Parameters:**
- `trend_data` (dict): Metric name as key, list of values as value
- `periods` (list[str]): Period labels
- `title` (str, optional): Chart title

**Returns:**
- `go.Figure`: Plotly figure

---

### `export_chart_to_html(fig: go.Figure, output_path: str) -> str`

Export interactive chart to standalone HTML file.

**Parameters:**
- `fig` (go.Figure): Plotly figure
- `output_path` (str): Output file path

**Returns:**
- `str`: Path to exported file

**Example:**
```python
fig = create_hygiene_gauge(85, {})
export_chart_to_html(fig, "data/reports/hygiene_chart.html")
```

---

### `create_dashboard_layout(charts: list[go.Figure], layout: str = 'grid', cols: int = 2) -> go.Figure`

Combine multiple charts into single dashboard.

**Parameters:**
- `charts` (list[go.Figure]): List of Plotly figures
- `layout` (str, optional): Layout type (grid | vertical | horizontal)
- `cols` (int, optional): Number of columns for grid layout

**Returns:**
- `go.Figure`: Combined dashboard figure

---

## Common Patterns

### Database Session Management

All analytics and insights functions handle database sessions internally:

```python
from src.db import get_postgres_session

session = get_postgres_session()
try:
    # Query operations
    accounts = session.query(GLAccount).filter_by(entity=entity).all()
finally:
    session.close()  # Always close session
```

### Error Handling

All functions return error dicts instead of raising exceptions:

```python
result = perform_analytics("Entity001", "2024-03")
if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(f"Success: {result['total_balance']}")
```

### Empty Data Handling

Functions gracefully handle empty data:

```python
result = calculate_variance_analysis("Entity999", "2024-03", "2024-02")
# Returns: {'error': 'No accounts found for Entity999 in period 2024-03'}
```

---

## Error Handling

### Common Error Types

1. **No Data Found**: `{'error': 'No accounts found for <entity> in period <period>'}`
2. **Database Connection**: `{'error': 'Database connection failed: <details>'}`
3. **Invalid Parameters**: `{'error': 'Invalid dimension: <dimension>'}`
4. **Calculation Error**: `{'error': 'Failed to calculate: <details>'}`

### Best Practices

1. Always check for `'error'` key in returned dict
2. Use try-except when calling functions
3. Provide fallback UI for errors
4. Log errors to `logs/app.log` for debugging

```python
try:
    result = perform_analytics(entity, period)
    if 'error' in result:
        st.error(f"Analytics Error: {result['error']}")
    else:
        st.success(f"Analyzed {result['account_count']} accounts")
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    logging.exception("Analytics failed")
```

---

## Dependencies

### Required Packages
- `pandas >= 2.0.0`
- `sqlalchemy >= 2.0.0`
- `pymongo >= 4.5.0`
- `plotly >= 5.17.0`
- `scipy >= 1.11.0` (for anomaly detection)
- `openpyxl >= 3.1.0` (for Excel export)

### Installation
```bash
conda env update -f environment.yml --prune
```

---

## Performance Notes

- **Analytics functions**: Optimized for <500ms with 501 accounts
- **Visualization rendering**: <2s per chart
- **Database queries**: Use indexes on `entity`, `period`, `account_code`
- **Memory usage**: < 100MB for typical operations

---

## Support

For issues or questions:
1. Check logs in `logs/app.log`
2. Review test cases in `tests/`
3. Consult `docs/Architecture.md`
4. Contact project maintainers

---

**Document Version:** 1.0.0
**Generated:** 2024
**Project:** Aura - AI-Powered Financial Review Agent
