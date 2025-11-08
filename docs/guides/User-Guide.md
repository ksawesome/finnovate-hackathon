# User Guide - Project Aura

**AI-Powered Financial Statement Review Agent**

Version 1.0.0 | Finnovate Hackathon 2024

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Feature Walkthroughs](#feature-walkthroughs)
5. [Common Workflows](#common-workflows)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Introduction

**Project Aura** is an intelligent financial review agent designed to automate and streamline GL (General Ledger) account validation, consolidation, and reporting for large-scale finance operations.

### Key Benefits

✅ **Automated Analysis**: Instant insights on 500+ GL accounts
✅ **Anomaly Detection**: ML-powered identification of unusual patterns
✅ **Proactive Alerts**: Smart recommendations based on data quality
✅ **Natural Language Queries**: Ask questions in plain English
✅ **Comprehensive Reporting**: Export-ready analytics and visualizations
✅ **Multi-Period Trending**: Track changes over time automatically

### Who Should Use This?

- **Finance Managers**: Executive summaries and hygiene scores
- **GL Reviewers**: Pending items and workload management
- **Controllers**: Variance analysis and compliance tracking
- **Auditors**: Documentation status and anomaly reports
- **Finance Leaders**: Strategic insights and trend analysis

---

## Getting Started

### Prerequisites

1. **Software Requirements**
   - Python 3.11+
   - PostgreSQL 14+ (running)
   - MongoDB 6+ (running)
   - Modern web browser (Chrome, Firefox, Edge)

2. **Environment Setup**
   ```powershell
   # Clone repository
   git clone <repository-url>
   cd finnovate-hackathon

   # Create conda environment
   conda env update -f environment.yml --prune
   conda activate finnovate-hackathon

   # Initialize databases
   .\scripts\local_db_setup.ps1
   ```

3. **Configuration**
   - Copy `.env.example` to `.env`
   - Set database credentials
   - Add `GOOGLE_API_KEY` for AI Assistant (optional)

### Launching the Application

```powershell
streamlit run src/app.py
```

The app will open at `http://localhost:8501`

---

## User Interface Overview

### Main Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Project Aura Logo                          [Entity] [Period]│
│  ─────────────────────────────────────────────────────────  │
│  │                    │                                      │
│  │  SIDEBAR           │     MAIN CONTENT AREA               │
│  │  ────────          │     ─────────────────               │
│  │  🏢 Entity &       │                                      │
│  │     Period         │     Page-specific content            │
│  │                    │     (charts, tables, forms)          │
│  │  📊 Quick Stats    │                                      │
│  │     - Total Acc.   │                                      │
│  │     - Balance      │                                      │
│  │                    │                                      │
│  │  Navigation        │                                      │
│  │  ○ Home            │                                      │
│  │  ○ Dashboard       │                                      │
│  │  ○ Analytics       │                                      │
│  │  ○ Lookup          │                                      │
│  │  ○ Reports         │                                      │
│  │  ○ AI Assistant    │                                      │
│  │  ○ Settings        │                                      │
└─────────────────────────────────────────────────────────────┘
```

### Navigation Pages

| Icon | Page | Purpose |
|------|------|---------|
| 🏠 | **Home** | Executive summary & quick overview |
| 📊 | **Dashboard** | Interactive charts & visualizations |
| 🔍 | **Analytics** | Deep-dive analysis & drill-downs |
| 🔎 | **Lookup** | Search & view individual GL accounts |
| 📄 | **Reports** | Generate & export reports |
| 🤖 | **AI Assistant** | Natural language queries |
| ⚙️ | **Settings** | Configuration & system status |

---

## Feature Walkthroughs

### 1. Home Page - Executive Overview

**Purpose**: Get a high-level view of GL health in under 30 seconds.

**Key Components**:

1. **Overall Status Banner**
   - Color-coded status: Excellent (green), Good (blue), Fair (orange), Needs Attention (red)
   - Based on hygiene score and completion rate

2. **Key Metrics Row**
   - Total Accounts
   - Total Balance (in ₹)
   - Hygiene Score (/100)
   - Completion Rate (%)

3. **Highlights Section** ✅
   - Lists positive indicators
   - Example: "95% of high-priority accounts reviewed"
   - Shows what's working well

4. **Areas of Concern** ⚠️
   - Lists items needing attention
   - Example: "15 accounts missing supporting documentation"
   - Prioritized by impact

5. **Recommendations** 💡
   - Actionable next steps
   - Example: "Focus on Assets category - 10 pending reviews"

6. **GL Hygiene Gauge**
   - Visual gauge showing 0-100 score
   - Color-coded zones (red/yellow/green)
   - Component breakdown below

**Workflow**:
```
1. Select entity & period in sidebar
2. Review overall status
3. Check key metrics
4. Read top 3 concerns
5. Take action on recommendations
```

---

### 2. Dashboard - Visual Analytics

**Purpose**: Explore data through interactive charts.

**Three Tabs**:

#### Tab 1: Overview
- **Category Breakdown** (Pie Chart)
  - Shows balance distribution by category
  - Click slices for details
  - Hover for exact amounts

- **Review Status** (Sunburst Chart)
  - Hierarchical view: Criticality → Status
  - Interactive drill-down
  - Color-coded by status

#### Tab 2: Variance Analysis
- **Waterfall Chart**
  - Shows top 15 variances
  - Green = positive, Red = negative
  - Compares current vs previous period

- **Variance Table**
  - Detailed breakdown
  - Sortable columns
  - Filter by significance

**Usage**:
```
1. Navigate to Dashboard page
2. Select "Variance Analysis" tab
3. Choose previous period for comparison
4. Review waterfall chart
5. Click "Generate Report" to export
```

#### Tab 3: Anomaly Detection
- **Z-Score Scatter Plot**
  - Balance vs Z-Score
  - Color by category
  - Size by anomaly severity

- **Adjustable Threshold Slider**
  - 1.5 = Sensitive (more alerts)
  - 2.0 = Balanced (recommended)
  - 3.0 = Conservative (fewer alerts)

- **Anomaly Table**
  - Account code, name, z-score
  - Severity classification
  - Category grouping

**Best Practice**: Start with threshold 2.0, adjust if too many/few alerts.

---

### 3. Analytics - Deep Dive Analysis

**Purpose**: Perform targeted analysis on specific dimensions.

**Three Tabs**:

#### Tab 1: Drill-Down
**Use Case**: "Show me all Assets accounts"

Steps:
1. Select dimension (Category, Department, Criticality, Review Status)
2. Enter filter value (e.g., "Assets")
3. Click "Analyze"
4. Review:
   - Summary metrics (count, balance, completion %)
   - Status distribution
   - Top 10 accounts by balance

**Example Queries**:
- "All High criticality accounts"
- "Finance department accounts"
- "Pending review accounts"
- "Expenses category"

#### Tab 2: Multi-Period Comparison
**Use Case**: "How have metrics changed over 3 months?"

Steps:
1. Select 2-5 periods to compare
2. Click "Compare Periods"
3. Review trend line chart
4. Check trend direction indicators:
   - 📈 Increasing (≥ +5%)
   - 📉 Decreasing (≤ -5%)
   - ➡️ Stable (-5% to +5%)

**Metrics Tracked**:
- Total Balance
- Hygiene Score
- Completion Rate
- Account Count

#### Tab 3: Pending Items
**Use Case**: "What needs my attention today?"

Automatically shows:
- **Pending Reviews** (by criticality)
- **Missing Documentation** (by due date)
- **Flagged Items** (by severity)

Each item includes:
- Account code & name
- Criticality level
- Days overdue (if applicable)
- Recommended action

**Action Items**:
```
1. Sort by criticality (High → Medium → Low)
2. Review top 5 items
3. Note account codes
4. Use Lookup page for details
5. Update status in source system
```

---

### 4. Lookup - Account Search

**Purpose**: Find and view details for specific GL accounts.

**Search Options**:
- By account code (exact or partial)
- By account name (keyword search)
- Case-insensitive

**Example Searches**:
- `100000` → Find account 100000
- `Cash` → Find all accounts with "Cash" in name
- `Bank` → Find bank-related accounts

**Account Detail View**:

Left Column:
- Category
- Department
- Criticality
- Debit Balance
- Credit Balance

Right Column:
- Review Status
- Reviewed By
- Reviewed At
- Comments

**Tips**:
- Search shows top 10 results
- Click expandable cards for full details
- Use specific codes for exact matches
- Use keywords for broader search

---

### 5. Reports - Export & Generation

**Purpose**: Generate formatted reports for distribution.

**Available Reports**:

1. **Executive Summary**
   - Overall status, metrics, highlights, concerns
   - Best for: Leadership, monthly reporting

2. **Variance Analysis**
   - Period-over-period changes
   - Best for: Controllers, variance reviews

3. **Anomaly Report**
   - Statistical outliers and unusual patterns
   - Best for: Auditors, risk teams

4. **Pending Items**
   - Action items by priority
   - Best for: GL reviewers, task tracking

5. **Full Analytics**
   - Comprehensive data dump
   - Best for: Data analysis, archival

**Export Formats**:
- **CSV**: For Excel, data analysis
- **Excel**: For formatted reports (coming soon)

**Workflow**:
```
1. Select report type
2. Choose export format
3. Click "Generate Report"
4. Review preview
5. Download file
```

**Output Location**: `data/reports/report_<type>_<timestamp>.csv`

---

### 6. AI Assistant - Natural Language Queries

**Purpose**: Ask questions about GL accounts in plain English.

**Setup** (First Time):
1. Ensure `GOOGLE_API_KEY` is set in `.env`
2. App will initialize agent on first visit
3. Wait for "AI Agent ready!" confirmation

**Example Questions**:

**Basic Queries**:
- "What is the total balance for Entity001?"
- "How many accounts are pending review?"
- "What is the hygiene score?"

**Comparative Queries**:
- "Which accounts have the largest variances?"
- "Show me the top 5 accounts by balance"
- "Compare Assets vs Liabilities"

**Status Queries**:
- "What accounts need documentation?"
- "List all flagged accounts"
- "Show pending high-priority reviews"

**Trend Queries**:
- "How has the hygiene score changed?"
- "What is the completion rate trend?"

**Response Format**:
```
You: What are the top 5 accounts with largest variances?

Aura: Based on the variance analysis for Entity001 in 2024-03:

1. Account 100000 (Cash): +₹50,000 (+33%)
2. Account 200000 (Accounts Payable): -₹20,000 (-15%)
3. Account 300000 (Inventory): +₹30,000 (+25%)
...

Recommendation: Review accounts with >20% variance for accuracy.
```

**Tips**:
- Be specific with entity and period
- Use clear, simple language
- Ask one question at a time
- Refer to displayed metrics for context

---

### 7. Settings - Configuration

**Database Connection Status**:
- PostgreSQL: Shows total accounts
- MongoDB: Shows audit record count

**Notification Preferences** (Future):
- Email alerts for critical items
- Daily summary reports
- Anomaly notifications
- Alert thresholds

**About Section**:
- Version information
- Technology stack
- Feature list
- Contact information

---

## Common Workflows

### Workflow 1: Daily Review (5 minutes)

**Goal**: Check overall health and address critical items

```
1. Home Page
   - Review overall status
   - Note hygiene score
   - Read top 3 concerns

2. Analytics → Pending Items
   - Check pending reviews count
   - Identify missing docs
   - Note flagged items

3. Lookup
   - Search flagged accounts
   - Review details
   - Document actions needed

4. Reports
   - Generate Pending Items report
   - Export for follow-up
```

**Expected Outcome**: Prioritized action list for the day

---

### Workflow 2: Monthly Variance Review (15 minutes)

**Goal**: Understand period-over-period changes

```
1. Dashboard → Variance Analysis
   - Select previous month
   - Review waterfall chart
   - Identify top 10 variances

2. Analytics → Drill-Down
   - Filter by category with large variance
   - Review affected accounts
   - Check status of each

3. Lookup
   - Search specific accounts
   - Verify balances
   - Check supporting docs

4. Reports
   - Generate Variance Report
   - Export for management review

5. AI Assistant
   - Ask: "What caused the variance in [category]?"
   - Get contextual insights
```

**Expected Outcome**: Variance explanation memo

---

### Workflow 3: Quarter-End Close (30 minutes)

**Goal**: Ensure all accounts ready for close

```
1. Home Page
   - Verify status = "Excellent" or "Good"
   - Confirm hygiene score ≥ 85
   - Check completion rate ≥ 95%

2. Analytics → Pending Items
   - Ensure 0 pending high-priority reviews
   - Verify all docs present
   - Resolve flagged items

3. Dashboard → Anomaly Detection
   - Run with threshold 2.0
   - Investigate all critical anomalies
   - Document resolutions

4. Analytics → Multi-Period Comparison
   - Compare last 3 months
   - Verify stable trends
   - Flag unusual patterns

5. Reports
   - Generate Executive Summary
   - Generate Full Analytics
   - Archive for auditors

6. Settings
   - Verify DB connectivity
   - Check audit record count
```

**Expected Outcome**: Close-ready accounts with documentation

---

### Workflow 4: New User Onboarding (10 minutes)

**Goal**: Learn the system quickly

```
1. Home Page (2 min)
   - Understand status indicators
   - Review key metrics
   - Read one insight

2. Dashboard (3 min)
   - Explore pie chart (click slices)
   - Try variance tab (change period)
   - Adjust anomaly threshold

3. Lookup (2 min)
   - Search "Cash"
   - Open account detail
   - Note information available

4. AI Assistant (3 min)
   - Ask: "What is the total balance?"
   - Ask: "How many pending reviews?"
   - Observe response format
```

**Expected Outcome**: Comfortable navigating all pages

---

## Tips & Best Practices

### Performance Tips

1. **Entity & Period Selection**
   - Change entity/period in sidebar affects all pages
   - Allow 1-2 seconds for data refresh
   - Use Quick Stats to verify correct entity

2. **Large Datasets**
   - Charts limited to top 15-20 items for speed
   - Use filters to narrow scope
   - Export to CSV for full data

3. **Browser Recommendations**
   - Chrome or Edge preferred
   - Enable JavaScript
   - Clear cache if charts don't load

### Data Quality Tips

1. **Hygiene Score Interpretation**
   - ≥ 85: Excellent (green zone)
   - 70-84: Good (yellow zone)
   - < 70: Needs attention (red zone)
   - Focus on lowest component score

2. **Variance Thresholds**
   - Significant = >10% OR >₹50,000
   - Adjust in code if needed for entity size
   - Track variance trends over time

3. **Anomaly Detection**
   - Z-score 2.0 = recommended starting point
   - Increase to 2.5 or 3.0 if too many false positives
   - Always investigate critical anomalies

### Workflow Tips

1. **Daily Routine**
   - Morning: Check Home page
   - Mid-day: Review Pending Items
   - End-of-day: Update statuses

2. **Weekly Routine**
   - Monday: Multi-period trend review
   - Wednesday: Drill-down by department
   - Friday: Generate executive summary

3. **Monthly Routine**
   - Week 1: Variance analysis vs prior month
   - Week 2: Documentation completeness check
   - Week 3: Anomaly review and resolution
   - Week 4: Quarter prep (if applicable)

### Reporting Tips

1. **For Management**
   - Use Executive Summary report
   - Include hygiene score trend chart
   - Highlight top 3 concerns

2. **For Reviewers**
   - Use Pending Items report
   - Sort by criticality
   - Include due dates

3. **For Auditors**
   - Use Anomaly Report
   - Include variance analysis
   - Attach documentation status

---

## Troubleshooting

### Issue: "No accounts found" error

**Possible Causes**:
- Wrong entity or period selected
- No data ingested for that combination
- Database connectivity issue

**Solutions**:
1. Verify entity/period in sidebar
2. Check Quick Stats shows data
3. Go to Settings → Database Status
4. Contact admin if persistent

---

### Issue: Charts not loading

**Possible Causes**:
- Browser JavaScript disabled
- Network issue
- Large dataset timing out

**Solutions**:
1. Refresh page (F5)
2. Enable JavaScript in browser
3. Try smaller date range
4. Clear browser cache

---

### Issue: AI Assistant not responding

**Possible Causes**:
- GOOGLE_API_KEY not set
- Network connectivity
- API quota exceeded

**Solutions**:
1. Check `.env` file has `GOOGLE_API_KEY=<your-key>`
2. Restart Streamlit app
3. Check API quota in Google Cloud Console
4. Use manual analysis as fallback

---

### Issue: Slow performance

**Possible Causes**:
- Too many accounts (>1000)
- Complex queries
- Database not indexed

**Solutions**:
1. Filter by entity/period
2. Use Lookup for specific accounts
3. Export to CSV for offline analysis
4. Contact admin to add indexes

---

### Issue: Export fails

**Possible Causes**:
- Insufficient permissions
- Disk space full
- Invalid file path

**Solutions**:
1. Check `data/reports/` directory exists
2. Verify write permissions
3. Free up disk space
4. Use shorter file names

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + R` | Refresh page |
| `Ctrl + F` | Find in page |
| `Esc` | Close dropdown/modal |
| `Tab` | Navigate form fields |

---

## Getting Help

### Documentation
- **Architecture**: `docs/Architecture.md`
- **API Reference**: `docs/guides/API-Reference.md`
- **Storage Design**: `docs/Storage-Architecture.md`

### Logs
- Application logs: `logs/app.log`
- Database logs: Check PostgreSQL/MongoDB logs

### Support Contacts
- Technical Issues: [Support Email]
- Feature Requests: [GitHub Issues]
- General Questions: [Project Wiki]

---

## Appendix

### Glossary

- **GL Account**: General Ledger account
- **Hygiene Score**: 0-100 score measuring data quality
- **Z-Score**: Statistical measure of how unusual a value is
- **Variance**: Difference between two periods
- **Anomaly**: Statistical outlier in data
- **Criticality**: Priority level (High/Medium/Low)
- **SLA**: Service Level Agreement (deadline)

### Sample Entities

- Entity001: Sample entity with 501 accounts
- Entity002-005: Test entities

### Sample Periods

- 2024-03: Most recent period
- 2024-02: Previous month
- 2024-01: Two months ago

---

**Document Version:** 1.0.0
**Last Updated:** 2024
**Project:** Aura - AI-Powered Financial Review Agent
**Hackathon:** Finnovate 2024
