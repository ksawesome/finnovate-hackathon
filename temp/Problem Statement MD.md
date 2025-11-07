## Problem Statement # 2 : Automated Balance Sheet Assurance

Background
The Finance & Accounts teams across the Adani Group—managing over 1,000 plus legal
entities—invest substantial time in review the numbers of Financial Statements on a monthly,
quarterly, and annual basis. This process primarily involves the following key activities

```
 Assigning the Trail Report GL accounts to multiple stakeholders as per the
responsibility matrix
 Maker & checker matrix adherence
 GL Validations, checks and review of hygiene
 Verification of supporting for all the GL accounts.
 Analytical Review
```
Much of this work is repetitive and manual. With advances in AI, we can now imagine an
autonomous review agent that gathers the data, validates it, and produces ready-to-use
reports and insights for leadership.

The Challenge

Build an AI Agent (put a cool name ) that that covers the end-to-end lifecycle of review of
Financial Statement numbers

```
 Collecting the data from multiple sources (spreadsheets, databases, ERPs, emails).
 Consolidating and cleaning data.
 Generating the draft reports
 Applying checks for accuracy and compliance.
 Providing interactive insights via dashboards or conversational interface.
```
# Core Capabilities

1. Data Ingestion & Consolidation

```
 Create one tool which can extract the company-wise trial report from multiple SAP
servers on daily basis
 Assign the user name /person responsibility (Name, department, e mail ID) against
each GL accounts based on the master responsibility matrix
 In case of NON-SAP entities, the input template needs to be created for manual trial
report uploading in the tool
 Auto e-mail to each user for uploading the supporting document against each gl.
 Auto e-mail to reviewer post the supporting / back up working file uploaded by the
users
 Auto e-mail to Business FC post the GL account reviewed by the reviewer
 Auto e-mail to each user post the GL account reviewed by Business FC
```

2. Automated Report Generation

```
 Generate exhaustive reports covering the following
o The status of numbers of GL accounts for which back up / supporting working
is pending to be uploaded in the tool
o The status of numbers of GL accounts reviewed by respective stakeholder &
number of accounts pending to be reviewed
o Deviation with respect to the assigned timeline
o Graphical presentation of hygiene of overall GL accounts
o Major GL variances compared to last month / quarter
```
```
 Produce both tabular and visual summaries (charts, graphs).
 Automated report generation based the special user queries
```
3. Validation & Compliance Checks

```
 The responsibility hierarchy based the authorisation so that the relevant person can
only login
 Ensure that total of trial report is Nil.
 The numbers as per the working file / supported file uploaded should match with the
GL account
 Post trial report extraction and supporting uploaded by users / review, in case of any
change in GL account balance, the same needs to be highlighted to User & Reviewer
immediately
```
4. Continuous Learning Loop

```
 Learn common reporting errors / mismatches
 Improve accuracy with human feedback: “This line item is new” → model learns
correction.
```
5. Agentic Behaviour

```
 Work like a reporting assistant: autonomously collect, compile, draft, and summarize.
 Proactively surface insights:
o “ Expense for the current period if X times the expenses of previous month /
quarter / year
```
6. Interactive Visualization

```
 Dashboard for drill-down (e.g., Profit, Assets by business unit, Company-wise various
data).
 Conversational interface to query reports: “Show me year - over-year Profit of Adani
Ports.”
```

# Why It Matters

```
 Reduces manual reporting / benchmarking effort and cycle time.
 Ensures accuracy, consistency, and transparency.
 Frees finance teams to focus on analysis instead of data wrangling.
 Turns Review and benchmarking from a backward-looking process into a real-time,
AI-driven insight engine.
```
# Tech Guidance (just sample – feel free to use what you

# want)

```
 Data Ingestion: Pandas, Apache Airflow, Power Query, Fivetran.
 Report Generation: Python (Pandas, Matplotlib, Plotly), Power BI, Tableau,
Streamlit.
 Validation: SQL rules, Great Expectations (data quality checks).
 Learning: scikit-learn, PyTorch, simple classification models retrained on
adjustments.
 Agent Frameworks: LangChain, LlamaIndex, Copilot Studio.
 Interfaces: Streamlit dashboards, Power BI reports, Teams/Slack chatbot for queries.
```
# Expected Output (Hackathon Prototype)

```
 Upload or connect to sample datasets (CSV/Excel/ERP exports).
 AI Agent ingests, consolidates, and generates draft reports.
 Dashboard or conversational interface presents key numbers, charts, and anomalies.
 Evidence of learning from user corrections (e.g., improving category accuracy).
```

