# Trial Balance Sample Data Analysis

**Date**: November 7, 2025  
**File**: `data/sample/Trial Balance with Grouping - V0.xlsx`  
**Total Sheets**: 12

---

## Executive Summary

This document provides a comprehensive analysis of the Trial Balance Excel workbook containing financial data for the Adani Group's GL account review process. The workbook contains 12 sheets with varying purposes - from summary dashboards to detailed transaction data.

### Key Findings:

- **Primary Data Sheet**: "Final Data" (502 records, 29 columns) - Core trial balance data
- **Summary Dashboard**: "Summary" sheet with review status by account categories
- **Multiple Versions**: Backup and old versions preserved (Final Data Backup, Final Data - Old)
- **Entity-Specific**: AGEL sheet contains entity-specific data
- **Data Quality Issues**: Several columns with significant null values (26-33%)
- **Review Flags**: Green/Red flags indicating review completion status

---

## Sheet-by-Sheet Analysis

### 1. Summary Sheet
**Purpose**: High-level dashboard showing GL account review status

**Structure**:
- **Dimensions**: 93 rows × 4 columns
- **Key Metrics**: Count of GL accounts by review status
- **Categories**:
  - Flag (Green/Red) - Review completion indicator
  - Main Head - Major account categories
  - Review Checkpoint - Validation points at ABEX
  - Total - Count aggregations

**Notable Features**:
- Groups accounts by main categories (Bank Balances, Capital WIP, Cash Equivalents, etc.)
- Tracks review checkpoint progress
- High null percentage (88.2% in col 0) suggests sparse formatting/grouping

**Sample Categories Found**:
- Bank Balances
- Capital Work in Progress
- Cash and Cash Equivalent
- Current Assets
- Current Liabilities
- Deposits
- Fixed Assets
- Provisions

**Quality Notes**:
- Contains process documentation (bonus handling, TDS reconciliation)
- Last rows (90-92) contain procedural notes

---

### 2. Final Data Sheet ⭐ **PRIMARY DATA SOURCE**
**Purpose**: Complete trial balance with all GL accounts and review metadata

**Structure**:
- **Dimensions**: 502 records × 29 columns
- **Data Coverage**: Comprehensive GL account listing with balances and review status

**Key Columns Identified**:
1. **BS/PL** - Balance Sheet or Profit & Loss classification
2. **Status** - Account status (Assets, Liabilities, Expense, Income)
3. **G/L Acct** - GL Account Number (8-digit codes)
4. **G/L Account Number** - Duplicate numeric field (some nulls - 26.1%)
5. **G/L Account Description** - Account names
6. **Balance Fields** - Multiple balance columns (APL Balance as on 30.06.2022)
7. **Flag (Green/Red)** - Review completion status
   - Green: Reviewed and approved
   - Red: Issues/pending
   - Not Considered: Skipped for this review cycle
8. **Type of Report** - Supporting documentation type (Inventory report, Fixed asset report, Working, etc.)
9. **Analysis Required** - Yes/No flag
10. **Review Check point at ABEX** - Validation performed

**Account Number Range**: 11100200 - 58003000 (8-digit format)

**Account Categories**:
- **Assets**: 11100200-series (Inventory, Stores & Spares)
- **Liabilities**: 21100000-series
- **Expenses**: 57001000-series (Depreciation, Deferred Tax)

**Data Quality Issues**:
- Unnamed columns (multiple) - Need proper header mapping
- Null values in G/L Acct Number: 26.1%
- Null values in column 20: 32.5%
- Null values in Balance column 24: 25.9%

**Sample Records**:

| BS/PL | Status  | GL Account | Description                                  | Balance (Jun'22) | Flag          |
|-------|---------|------------|----------------------------------------------|------------------|---------------|
| BS    | Assets  | 11100200   | Stock of Capital Inventory-Domestic          | 3,531,804.53     | Red           |
| BS    | Assets  | 11100400   | Stock of Stores & Spares-Domestic            | 6,102,197.23     | Green         |
| PL    | Expense | 57001000   | Dep-Plnt & Mach                              | 71,393,154.33    | Not Considered|
| PL    | Expense | 57001100   | Dep-Furn & Fix                               | 983,720.83       | Not Considered|

**Statistical Summary (GL Account Numbers)**:
- Count: 371 valid account numbers
- Mean: 31,611,870
- Min: 11,100,200
- Max: 58,003,000
- 25th percentile: 12,103,220
- Median: 21,199,120
- 75th percentile: 52,004,050

---

### 3. Sheet2 - Risk Pivot Analysis
**Purpose**: Pivot/summary analysis by sub-head and criticality

**Structure**:
- **Dimensions**: 11 rows × 5 columns
- **Type**: Appears to be a pivot table summary

**Categories**:
- **Criticality Levels**: Critical, Low, Medium
- **Row Labels**: Names (possibly reviewers - Yash G mentioned)
- **Zero Balance**: 102 accounts with zero balance (77 critical, 4 low, 21 medium)
- **Grand Total**: 295 accounts tracked (153 critical, 12 low, 130 medium)

**Insight**: Helps prioritize review based on materiality/risk level

#### Relevance to Our Application:
This sheet demonstrates the **risk-based assignment strategy** we need to implement:

1. **Smart Assignment Algorithm**:
   - Use criticality scores to prioritize reviewer workload
   - Critical accounts get assigned to senior reviewers
   - Medium/Low accounts can be distributed to team members

2. **Dashboard Metrics**:
   - Show breakdown of accounts by criticality
   - Track zero-balance accounts separately (lower priority)
   - Display reviewer-wise workload distribution

3. **Zero Balance Handling**:
   - 102 zero-balance accounts still require review (dormant account validation)
   - ML model can learn to auto-flag zero-balance accounts as "low priority"
   - Agent can suggest skipping zero-balance GL codes based on historical patterns

#### How We Can Use It:
```python
# In src/analytics.py - Risk-based assignment
def assign_accounts_by_risk(df, reviewers):
    """Assign GL accounts to reviewers based on criticality"""
    critical = df[df['criticality'] == 'Critical']
    medium = df[df['criticality'] == 'Medium']
    low = df[df['criticality'] == 'Low']
    
    # Senior reviewers get critical accounts
    assignments = {
        'senior_reviewer': critical,
        'reviewer_1': medium[:len(medium)//2],
        'reviewer_2': medium[len(medium)//2:],
        'junior_reviewer': low
    }
    return assignments
```

---

### 4. Main Sheet - Extended Working Data
**Purpose**: Detailed working sheet with extended metadata

**Structure**:
- **Dimensions**: 304 records × 22 columns
- **Scope**: Subset of Final Data with additional working columns

**Analysis Required**: Further investigation needed to understand relationship with Final Data

#### Relevance to Our Application:
This is a **working sheet** used during the review process, showing:

1. **Work-in-Progress Tracking**:
   - Subset of 304 accounts (out of 501 total) suggests active review batch
   - Additional columns likely contain reviewer notes, intermediate calculations
   - Demonstrates need for "session-based" review workflow

2. **Batch Processing Pattern**:
   - Not all accounts reviewed simultaneously
   - Accounts processed in batches based on department/category
   - System should support "save progress" and "resume review" functionality

3. **Audit Trail Requirements**:
   - Shows evolution of review from raw data to final approval
   - Need to track: who reviewed, when, what changes made
   - MongoDB audit_trail collection should capture this workflow

#### How We Can Use It:
```python
# In src/db/mongodb.py - Track review sessions
def create_review_session(user_id, gl_codes, session_type='batch'):
    """Create a review session for batch processing"""
    session = {
        'session_id': generate_session_id(),
        'user_id': user_id,
        'gl_codes': gl_codes,
        'session_type': session_type,  # 'batch', 'entity', 'category'
        'status': 'in_progress',
        'created_at': datetime.now(),
        'accounts_reviewed': 0,
        'accounts_pending': len(gl_codes)
    }
    get_audit_trail_collection().insert_one(session)
    return session['session_id']

# In src/app.py - Streamlit UI
def render_batch_review_page():
    """Allow reviewers to work on account batches"""
    st.header("Batch Review Session")
    
    # Load user's assigned batch (304 accounts pattern)
    batch = get_reviewer_batch(st.session_state.user_id)
    
    # Progress tracker
    progress = batch['accounts_reviewed'] / len(batch['gl_codes'])
    st.progress(progress)
    
    # Review interface with save/resume
    for gl_code in batch['gl_codes']:
        render_account_review_card(gl_code)
        if st.button(f"Save & Next ({gl_code})"):
            save_review_progress(batch['session_id'], gl_code)
```

---

### 5. Sheet3 - Assignment & Query Tracking
**Purpose**: Detailed assignment tracking with query types and working requirements

**Structure**:
- **Dimensions**: 166 records × 37 columns
- **Rich Metadata**: Assignment dates, person names, query types, working needed, comments

**Key Columns Identified**:
- **Assignment Fields**: Assignment Date, R Department, R Person Name (e.g., saurin.gandhi1@adani.com)
- **Status Tracking**: P.S (Prepare Status), R.S (Review Status), F.S (Final Status), Ok, Form Fill
- **Severity**: Severity classification for issues
- **GL Account Details**: GL Account, BPC G/L Acc, BPC G/L Acc Name, Category
- **Financial Metrics**: Amt Lc (Local Currency Amount), Reconciled Amt LC
- **Reclassification**: BS Reclassification LC, P&L Impact Amt LC
- **Query Management**: Query type, Working Needed, P Comment (Preparer), R Comment (Reviewer)
- **Overall Status**: Overall Reconciliation Status

**Notable Patterns**:
- 100% nulls in C.K, Assignment Date, Overall Reconciliation Status, Comments - suggests incomplete workflow
- All records show "Pending" status (P.S, R.S, F.S) - active review queue
- Single reviewer email (saurin.gandhi1@adani.com) for all 166 accounts
- Query types are very detailed (e.g., "Classification of Inventory between Opex and Capex")

#### Relevance to Our Application:
This is the **MOST CRITICAL SHEET** for implementing the agentic workflow:

1. **Assignment & Responsibility Matrix**:
   - Maps GL accounts to specific reviewers by email
   - Department-wise responsibility (R2R, O2C, B2P, TRM)
   - Shows real-world assignment patterns (one reviewer handling 166 accounts)
   - **Database Mapping**: Directly maps to `responsibility_matrix` table

2. **Multi-Stage Review Workflow**:
   - **P.S (Prepare Status)**: Initial data gathering phase
   - **R.S (Review Status)**: Reviewer validation phase
   - **F.S (Final Status)**: Approval/sign-off phase
   - **Form Fill**: Checklist completion
   - **Ok**: Final approval flag
   - System must support 5-stage workflow with status transitions

3. **Query Type Library**:
   - Pre-defined query types for common issues:
     - "Classification of Inventory between Opex and Capex"
     - "Old Non moving inventories lying and Provision"
     - "GL balance should match with working"
     - "Distribution shall be made at rate mentioned in Agreement"
   - **Agent Use Case**: Train LLM on these query types to auto-detect similar issues
   - **Knowledge Base**: Seed LangChain RAG with these queries

4. **Working Requirements**:
   - Each query type has associated deliverables:
     - "Inventory Ageing report"
     - "Working for Inventory reclassification"
     - "Board Resolution"
     - "Confirmation from vendor"
   - **Agent Capability**: Suggest required documents based on GL account type
   - **Document Management**: Link to `supporting_docs` MongoDB collection

5. **Reclassification Tracking**:
   - BS Reclassification LC (Balance Sheet adjustments)
   - P&L Impact Amt LC (Profit & Loss impact)
   - Critical for consolidation and financial reporting
   - **Validation Rule**: Reclassifications must net to zero

6. **Comment System**:
   - P Comment: Preparer/Maker comments
   - R Comment: Reviewer/Checker comments
   - **Maker-Checker Pattern**: Dual control workflow
   - Store in MongoDB for audit trail

#### How We Can Use It:
```python
# 1. In src/db/postgres.py - Populate responsibility matrix
def seed_responsibility_matrix_from_sheet3(sheet3_df):
    """Load reviewer assignments from Sheet3"""
    assignments = []
    for _, row in sheet3_df.iterrows():
        assignment = ResponsibilityMatrix(
            gl_code=str(row['GL Account']),
            assigned_user_id=get_user_id_by_email(row['R  Person Name']),
            department=row['R Department'],
            assignment_date=row['Assignment Date'] if pd.notna(row['Assignment Date']) else datetime.now(),
            status='pending',  # From P.S, R.S, F.S columns
            query_type=row['Query type'],
            working_needed=row['Working Needed'],
            severity=row['Severity']
        )
        assignments.append(assignment)
    session.bulk_save_objects(assignments)

# 2. In src/langchain_tools.py - Query type detection tool
class QueryTypeDetectionTool(BaseTool):
    name = "detect_query_type"
    description = "Detect common review query types for GL accounts"
    
    # Seed from Sheet3 query types
    KNOWN_QUERIES = [
        "Inventory classification (Opex vs Capex)",
        "Non-moving inventory provision",
        "GL balance reconciliation with working",
        "Distribution approval verification",
        "Zero balance validation",
        "Related party transaction confirmation"
    ]
    
    def _run(self, gl_code: str, account_description: str) -> str:
        """Use embeddings to match against known query types"""
        # RAG implementation using ChromaDB
        query_embedding = get_embedding(account_description)
        similar_queries = vector_store.similarity_search(
            query_embedding, 
            collection="query_types"
        )
        return similar_queries[0] if similar_queries else "General review"

# 3. In src/agent.py - Multi-stage workflow agent
def create_review_workflow_agent():
    """Agent that manages P.S → R.S → F.S workflow"""
    
    workflow_prompt = """
    You are managing a multi-stage GL account review workflow:
    
    Stage 1 (P.S - Prepare): 
    - Gather required documents (inventory reports, reconciliations)
    - Perform initial analysis
    - Flag potential issues
    
    Stage 2 (R.S - Review):
    - Validate preparer's work
    - Check calculations
    - Request additional evidence if needed
    
    Stage 3 (F.S - Final):
    - Approve or reject review
    - Document final decision
    - Escalate critical issues
    
    Current stage: {stage}
    GL Account: {gl_code}
    Query Type: {query_type}
    Working Needed: {working_needed}
    
    What action should be taken next?
    """
    
    tools = [
        QueryTypeDetectionTool(),
        DocumentRetrievalTool(),
        CalculationValidationTool(),
        EscalationTool()
    ]
    
    return create_agent(tools=tools, prompt=workflow_prompt)

# 4. In src/app.py - Reviewer dashboard
def render_reviewer_workload():
    """Show reviewer's assigned accounts (like 166 accounts in Sheet3)"""
    st.header(f"Your Assigned Accounts - {st.session_state.user_name}")
    
    # Query responsibility_matrix
    assignments = get_user_assignments(st.session_state.user_id)
    
    # Group by status
    pending_ps = [a for a in assignments if a.status == 'pending_prepare']
    pending_rs = [a for a in assignments if a.status == 'pending_review']
    pending_fs = [a for a in assignments if a.status == 'pending_final']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Prepare Stage", len(pending_ps))
    col2.metric("Review Stage", len(pending_rs))
    col3.metric("Final Stage", len(pending_fs))
    
    # Show severity breakdown
    critical = len([a for a in assignments if a.severity == 'Critical'])
    st.error(f"⚠️ {critical} Critical accounts require attention")
    
    # Filterable table with query types
    df = pd.DataFrame([{
        'GL Account': a.gl_code,
        'Status': a.status,
        'Severity': a.severity,
        'Query Type': a.query_type,
        'Working Needed': a.working_needed,
        'Assignment Date': a.assignment_date
    } for a in assignments])
    
    st.dataframe(df, use_container_width=True)

# 5. In src/insights.py - Query type analytics
def analyze_common_queries():
    """Identify most common query types across entities"""
    query_counts = {}
    
    # Aggregate from Sheet3 data
    all_assignments = session.query(ResponsibilityMatrix).all()
    for assignment in all_assignments:
        query_type = assignment.query_type
        query_counts[query_type] = query_counts.get(query_type, 0) + 1
    
    # Find patterns
    top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Train ML model on these patterns
    # Agent can proactively suggest query types for new accounts
    return top_queries
```

**Integration with Great Expectations**:
```python
# In src/data_validation.py
def create_sheet3_validation_suite():
    """Validate assignment data integrity"""
    suite = context.add_expectation_suite(suite_name="assignment_validation")
    
    expectations = [
        # All accounts must have assigned reviewer
        "expect_column_values_to_not_be_null(column='R  Person Name')",
        
        # Status must be valid
        "expect_column_values_to_be_in_set(column='P.S', value_set=['Pending', 'Complete'])",
        
        # Reclassifications must balance
        "expect_column_sum_to_equal(column='BS Reclassification  LC', value=0)",
        
        # Severity must be set for all records
        "expect_column_values_to_be_in_set(column='Severity', value_set=['Critical', 'Medium', 'Low'])"
    ]
    
    return suite
```

---

### 5. Sheet3 (Original) - Legacy Assignment Data
**Purpose**: Additional pivot/grouping analysis (Structure TBD)

---

### 6. Base File Sheet - Source of Truth
**Purpose**: Original source data before transformations

**Structure**:
- **Dimensions**: 2736 records × 13 columns (5x larger than Final Data!)
- **Coverage**: Complete chart of accounts before filtering

**Key Columns**:
- **G/L Acct**: Account code
- **G/L Account Description**: Account name
- **BS/PL**: Balance Sheet or P&L classification
- **Group GL Account**: Parent/grouping account
- **TB - 5500**: Trial Balance for entity 5500 (likely ABEX)
- **Reclassification_Mar-18**: Historical reclassification adjustments
- **Derived TB - 5500**: Adjusted trial balance after reclassifications
- **Sch. No.**: Schedule number for financial statements
- **Main Group / Sub Group**: Account categorization

**Notable Statistics**:
- **2736 total accounts** (vs 501 in Final Data) - 82% reduction
- Balance range: -100 billion to +107 billion (massive scale)
- 86.4% nulls in one column suggests data quality filtering needed
- Schedule numbers range 0-35 (financial statement sections)

**Importance**: 
- Maintains data lineage - shows complete account universe
- Allows validation of transformations from raw to Final Data
- Baseline for reconciliation between source system and review dataset
- Historical reclassifications provide audit trail

#### Relevance to Our Application:

1. **Master Data Management**:
   - This is the **complete chart of accounts** (2736 accounts)
   - Final Data (501 accounts) is a filtered subset for active review
   - System needs to maintain both:
     - **Active accounts**: In gl_accounts table for review workflow
     - **Master list**: Reference table for account lookups and validation

2. **Data Lineage & Reconciliation**:
   - **Source → Filtered → Review** pipeline validation
   - Formula: `Derived TB = TB + Reclassification`
   - Great Expectations suite should validate this transformation:
   ```python
   # Validation rule
   expect_column_pair_sum_to_equal(
       column_A="TB - 5500",
       column_B="Reclassification_Mar-18", 
       sum_column="Derived TB - 5500"
   )
   ```

3. **Group GL Account Hierarchy**:
   - Parent-child relationships for account grouping
   - Enables drill-down from summary to detail
   - **Dashboard Use Case**: Show revenue by category, then expand to individual accounts

4. **Historical Reclassification Tracking**:
   - "Reclassification_Mar-18" column shows past adjustments
   - ML model can learn patterns:
     - Which accounts frequently get reclassified?
     - Common reclassification amounts?
     - Predict future reclassification needs

5. **Schedule Number Mapping**:
   - Maps GL accounts to financial statement line items
   - **Sch. No.** links to published financial statements
   - Agent can answer: "Which accounts roll into Schedule 6 (Inventories)?"

#### How We Can Use It:

```python
# 1. In src/db/postgres.py - Create master account table
CREATE TABLE master_chart_of_accounts (
    id SERIAL PRIMARY KEY,
    account_code VARCHAR(50) NOT NULL UNIQUE,
    account_description VARCHAR(255),
    group_gl_account VARCHAR(50),  -- Parent account
    schedule_number INTEGER,       -- Financial statement line item
    main_group VARCHAR(100),
    sub_group VARCHAR(100),
    bs_pl VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,  -- Filtered to Final Data if TRUE
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# 2. In src/data_validation.py - Validate transformation pipeline
def validate_base_to_final_transformation():
    """Ensure Final Data accounts are subset of Base File"""
    
    base_accounts = set(base_file_df['G/L Acct'])  # 2736 accounts
    final_accounts = set(final_data_df['G/L Acct'])  # 501 accounts
    
    # All Final Data accounts must exist in Base File
    assert final_accounts.issubset(base_accounts), \
        f"Found {len(final_accounts - base_accounts)} orphan accounts"
    
    # Log filtering logic
    filtered_out = base_accounts - final_accounts  # 2235 accounts
    logger.info(f"Filtered out {len(filtered_out)} accounts (reasons: inactive, zero balance, low materiality)")
    
    # Validate reclassification math
    for _, row in base_file_df.iterrows():
        tb = row['TB - 5500']
        reclass = row['Reclassification_Mar-18']
        derived = row['Derived TB - 5500']
        
        if pd.notna(tb) and pd.notna(reclass) and pd.notna(derived):
            assert abs((tb + reclass) - derived) < 0.01, \
                f"Reclassification math error for {row['G/L Acct']}"

# 3. In src/langchain_tools.py - Account hierarchy navigation
class AccountHierarchyTool(BaseTool):
    name = "navigate_account_hierarchy"
    description = "Navigate parent-child GL account relationships"
    
    def _run(self, account_code: str, direction: str = "children") -> List[str]:
        """
        Get parent or child accounts
        direction: 'children' or 'parent'
        """
        if direction == "parent":
            # Find parent group account
            result = session.query(MasterChartOfAccounts).filter_by(
                account_code=account_code
            ).first()
            return [result.group_gl_account] if result else []
        
        else:  # children
            # Find all accounts with this as group_gl_account
            children = session.query(MasterChartOfAccounts).filter_by(
                group_gl_account=account_code
            ).all()
            return [child.account_code for child in children]

# 4. In src/visualizations.py - Hierarchical sunburst chart
def create_account_hierarchy_chart(schedule_number=None):
    """Create interactive sunburst chart of account hierarchy"""
    import plotly.express as px
    
    # Load base file with hierarchy
    df = load_base_file()
    
    if schedule_number:
        df = df[df['Sch. No.'] == schedule_number]
    
    # Create hierarchy: Main Group → Sub Group → GL Account
    fig = px.sunburst(
        df,
        path=['Main Group', 'Sub Group', 'G/L Account Description'],
        values='Derived TB - 5500',
        title=f"Account Hierarchy - Schedule {schedule_number}" if schedule_number else "Complete Account Hierarchy"
    )
    
    return fig

# 5. In src/analytics.py - Identify inactive accounts
def analyze_account_filtering():
    """Understand why 2235 accounts were filtered out"""
    
    base_codes = set(base_file_df['G/L Acct'])
    final_codes = set(final_data_df['G/L Acct'])
    filtered_codes = base_codes - final_codes
    
    # Analyze filtered accounts
    filtered_df = base_file_df[base_file_df['G/L Acct'].isin(filtered_codes)]
    
    reasons = {
        'zero_balance': len(filtered_df[abs(filtered_df['Derived TB - 5500']) < 0.01]),
        'no_schedule': len(filtered_df[filtered_df['Sch. No.'].isna()]),
        'unmapped_group': len(filtered_df[filtered_df['Main Group'].isna()]),
    }
    
    # ML model can learn: which accounts are review-worthy?
    # Features: balance magnitude, schedule number, historical activity
    train_active_account_classifier(filtered_df, final_data_df)
    
    return reasons

# 6. In src/agent.py - Schedule-based queries
def answer_schedule_query(schedule_number: int):
    """Agent answers questions like: 'What accounts are in Schedule 6?'"""
    
    accounts = session.query(MasterChartOfAccounts).filter_by(
        schedule_number=schedule_number,
        is_active=True
    ).all()
    
    response = f"Schedule {schedule_number} includes {len(accounts)} accounts:\n"
    
    # Group by category
    by_group = {}
    for acc in accounts:
        if acc.main_group not in by_group:
            by_group[acc.main_group] = []
        by_group[acc.main_group].append(acc.account_code)
    
    for group, codes in by_group.items():
        response += f"\n{group}: {', '.join(codes)}"
    
    return response
```

**Great Expectations Suite for Base File**:
```python
def create_base_file_validation_suite():
    """Validate base file data integrity"""
    
    suite = context.add_expectation_suite(suite_name="base_file_validation")
    
    expectations = [
        # All accounts must have unique codes
        "expect_column_values_to_be_unique(column='G/L Acct')",
        
        # Reclassification math must balance
        "expect_multicolumn_sum_to_equal(
            column_list=['TB - 5500', 'Reclassification_Mar-18'],
            sum_total='Derived TB - 5500',
            tolerance=0.01
        )",
        
        # BS/PL must be valid
        "expect_column_values_to_be_in_set(column='BS/PL', value_set=['BS', 'PL'])",
        
        # Schedule numbers must be valid range
        "expect_column_values_to_be_between(column='Sch. No.', min_value=0, max_value=35)",
        
        # Main Group should not be null for active accounts
        "expect_column_values_to_not_be_null(column='Main Group')"
    ]
    
    return suite
```

---

### 7. Sheet1 - Empty Placeholder
**Purpose**: Working/scratch sheet (Currently empty)

**Structure**:
- **Dimensions**: 0 rows × 0 columns
- **Type**: Empty DataFrame

#### Relevance to Our Application:
- Placeholder for ad-hoc analysis or temporary calculations
- Shows real-world Excel workflow: multiple working tabs
- **System Implication**: Support for "scratch pad" or "notes" functionality
- Users may want temporary calculation space that doesn't affect official data

#### How We Can Use It:
```python
# In src/app.py - Provide scratch pad feature
def render_scratch_pad():
    """Give users a temporary calculation space"""
    st.header("Scratch Pad - Temporary Calculations")
    st.info("This space is for your temporary work. Nothing here is saved to the database.")
    
    # Temporary dataframe editor
    if 'scratch_df' not in st.session_state:
        st.session_state.scratch_df = pd.DataFrame({
            'Account': [],
            'Calculation': [],
            'Notes': []
        })
    
    edited_df = st.data_editor(
        st.session_state.scratch_df,
        num_rows="dynamic",
        use_container_width=True
    )
    
    st.session_state.scratch_df = edited_df
    
    # Export to CSV if needed
    if st.button("Export Scratch Pad"):
        csv = edited_df.to_csv(index=False)
        st.download_button("Download CSV", csv, "scratch_pad.csv")
```

---

### 8. Sheet4 - Account Assignment List
**Purpose**: Simple GL account to reviewer mapping

**Structure**:
- **Dimensions**: 18 rows × 2 columns
- **Columns**: Account code (11312500) and Reviewer name (Kushang)
- **Pattern**: All 18 accounts assigned to single reviewer "Kushang"

**Account Range**: 11312510 - 21195100 (mix of asset and liability accounts)

#### Relevance to Our Application:

1. **Simplified Assignment Model**:
   - Contrast with Sheet3 (166 accounts, complex workflow)
   - Sheet4 shows **lightweight assignment**: just account + reviewer
   - Useful for bulk assignment or reassignment scenarios

2. **Reviewer Specialization**:
   - "Kushang" assigned specific account range (11312xxx - 21195xxx)
   - Suggests **account-based specialization** (reviewer expertise by GL code range)
   - Different from department-based assignment (Sheet3 model)

#### How We Can Use It:
```python
# In src/db/postgres.py - Bulk assignment function
def bulk_assign_accounts(gl_codes: List[str], reviewer_email: str):
    """Assign multiple accounts to one reviewer (Sheet4 pattern)"""
    
    user_id = get_user_id_by_email(reviewer_email)
    
    for gl_code in gl_codes:
        assignment = ResponsibilityMatrix(
            gl_code=gl_code,
            assigned_user_id=user_id,
            assignment_date=datetime.now(),
            status='pending',
            assignment_type='bulk'  # vs 'automated' or 'manual'
        )
        session.add(assignment)
    
    session.commit()
    logger.info(f"Bulk assigned {len(gl_codes)} accounts to {reviewer_email}")

# In src/app.py - Admin bulk assignment UI
def render_bulk_assignment_page():
    """Allow admins to assign accounts in bulk"""
    st.header("Bulk Account Assignment")
    
    # Input: Account range or list
    account_input = st.text_area(
        "Enter GL account codes (one per line)",
        placeholder="11312510\n11312600\n11312610"
    )
    
    # Select reviewer
    reviewers = get_all_reviewers()
    selected_reviewer = st.selectbox(
        "Assign to reviewer",
        options=[r.email for r in reviewers]
    )
    
    if st.button("Bulk Assign"):
        gl_codes = [line.strip() for line in account_input.split('\n') if line.strip()]
        bulk_assign_accounts(gl_codes, selected_reviewer)
        st.success(f"Assigned {len(gl_codes)} accounts to {selected_reviewer}")
```

---

### 9. Observations Sheet - Review Findings & Requirements
**Purpose**: Contains review comments, exceptions, system improvement suggestions

**Structure**:
- **Dimensions**: 37 rows × 13 columns
- **Type**: Unstructured observations and requirements

**Key Content Categories**:

1. **System Enhancement Requests**:
   - "Document currency to remove as base of analysis is INR only"
   - "PS - Prepare Status", "FF - Filed Form" (status definitions)
   - "Approver and Reviewer to incorporate"
   - "Attachment to add and make as optional"

2. **Dashboard Requirements**:
   - "Cards to change > GL Count, Total Assets, Total Liabilities, BS Impact, PnL Impact"
   - "Filters > Co Code to add, Main head and sub head to add and GL account to remove"
   - "User analysis > Company code and vertical to add"

3. **Workflow Improvements**:
   - "Attachment to add and make as optional"
   - "Dash board modifications based on PnL GL Codes"

**Notable Pattern**:
- 89.2% nulls in "Dashboard" column - sparse data structure
- Observations appear to be collected feedback from users
- Mix of technical requirements and business rules

#### Relevance to Our Application:

This sheet is **GOLD MINE** for product requirements! It shows:

1. **Real User Pain Points**:
   - Users want INR-only reporting (simplify currency handling)
   - Need for status definitions (P.S, FF) - build glossary
   - Attachment management is critical pain point

2. **Dashboard Feature Requests**:
   - Metrics needed: GL Count, Total Assets, Total Liabilities, BS Impact, P&L Impact
   - Filters needed: Company Code, Main Head, Sub Head
   - User-specific analytics views

3. **Workflow Gaps**:
   - Approver vs Reviewer roles need clarification
   - Attachment workflow needs improvement (optional vs required)
   - P&L-specific dashboard modifications

4. **Continuous Feedback Loop**:
   - Shows active user feedback collection
   - System evolves based on reviewer input
   - **ML Training Data**: User suggestions improve agent responses

#### How We Can Use It:

```python
# 1. In src/db/mongodb.py - Store user feedback
def log_user_observation(user_id: str, observation: str, category: str):
    """Capture user feedback like Observations sheet"""
    
    observation_doc = {
        'user_id': user_id,
        'observation': observation,
        'category': category,  # 'feature_request', 'bug', 'enhancement', 'process'
        'timestamp': datetime.now(),
        'status': 'new',  # 'new', 'reviewed', 'implemented', 'rejected'
        'priority': None,  # Set by product team
        'related_gl_codes': []
    }
    
    get_mongo_database()['user_feedback'].insert_one(observation_doc)

# 2. In src/app.py - Feedback widget on every page
def render_feedback_widget():
    """Allow users to submit observations (like Observations sheet)"""
    with st.expander("💡 Submit Feedback"):
        observation = st.text_area("What would improve your workflow?")
        category = st.selectbox(
            "Category",
            options=['Feature Request', 'Bug Report', 'Process Improvement', 'Dashboard Enhancement']
        )
        
        if st.button("Submit Observation"):
            log_user_observation(
                st.session_state.user_id,
                observation,
                category
            )
            st.success("Thank you! Your feedback has been recorded.")

# 3. In src/visualizations.py - Implement requested dashboard metrics
def create_executive_dashboard(period: str):
    """Dashboard metrics from Observations sheet requirements"""
    
    metrics = calculate_period_metrics(period)
    
    # Row 1: Core metrics (from Observations: "GL Count, Total Assets, Total Liabilities")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("GL Accounts", metrics['gl_count'])
    col2.metric("Total Assets", f"₹{metrics['total_assets']:,.0f}")
    col3.metric("Total Liabilities", f"₹{metrics['total_liabilities']:,.0f}")
    col4.metric("BS Impact", f"₹{metrics['bs_impact']:,.0f}")
    col5.metric("P&L Impact", f"₹{metrics['pl_impact']:,.0f}")
    
    # Row 2: Filters (from Observations: "Co Code, Main head, sub head")
    with st.container():
        fcol1, fcol2, fcol3 = st.columns(3)
        
        selected_company = fcol1.multiselect(
            "Company Code",
            options=get_company_codes()
        )
        
        selected_main_head = fcol2.multiselect(
            "Main Head",
            options=get_main_heads()
        )
        
        selected_sub_head = fcol3.multiselect(
            "Sub Head",
            options=get_sub_heads()
        )
    
    # Apply filters and show filtered data
    filtered_df = apply_filters(
        df,
        company_codes=selected_company,
        main_heads=selected_main_head,
        sub_heads=selected_sub_head
    )
    
    st.dataframe(filtered_df)

# 4. In src/app.py - Attachment management (from Observations: "Attachment to add")
def render_attachment_upload(gl_code: str, required: bool = False):
    """
    Upload supporting documents
    required: False per Observations sheet ("make as optional")
    """
    st.subheader("Supporting Documents")
    
    if required:
        st.warning("⚠️ At least one attachment is required to complete review")
    else:
        st.info("ℹ️ Attachments are optional but recommended")
    
    uploaded_files = st.file_uploader(
        "Upload supporting documents",
        accept_multiple_files=True,
        type=['pdf', 'xlsx', 'csv', 'png', 'jpg']
    )
    
    if uploaded_files:
        for file in uploaded_files:
            # Save to data/supporting_docs/
            file_path = save_supporting_document(gl_code, file)
            
            # Log to MongoDB
            log_document_upload(
                gl_code=gl_code,
                file_path=file_path,
                file_type=file.type,
                uploaded_by=st.session_state.user_id
            )
        
        st.success(f"Uploaded {len(uploaded_files)} document(s)")

# 5. In src/agent.py - Glossary for status codes (from Observations: "PS - Prepare Status")
STATUS_GLOSSARY = {
    'PS': 'Prepare Status - Initial data gathering and analysis phase',
    'RS': 'Review Status - Reviewer validation phase',
    'FS': 'Final Status - Approval and sign-off phase',
    'FF': 'Filed Form - Checklist completed',
    'Ok': 'Approved - Final approval granted'
}

def get_status_explanation(status_code: str) -> str:
    """Agent provides status definitions (addresses Observations feedback)"""
    return STATUS_GLOSSARY.get(status_code.upper(), "Unknown status code")

# 6. In src/insights.py - Analyze feedback trends
def analyze_user_feedback():
    """Generate insights from Observations-style feedback"""
    
    feedback = get_mongo_database()['user_feedback'].find()
    
    # Categorize feedback
    by_category = {}
    for item in feedback:
        cat = item['category']
        by_category[cat] = by_category.get(cat, 0) + 1
    
    # Identify common themes using NLP
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    
    texts = [item['observation'] for item in feedback]
    
    if len(texts) > 10:
        vectorizer = TfidfVectorizer(max_features=20, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        # Cluster similar feedback
        kmeans = KMeans(n_clusters=min(5, len(texts)//3))
        clusters = kmeans.fit_predict(X)
        
        # Top keywords per cluster
        for i in range(kmeans.n_clusters):
            cluster_texts = [texts[j] for j in range(len(texts)) if clusters[j] == i]
            st.write(f"**Feedback Theme {i+1}**: {len(cluster_texts)} observations")
            # Show sample
            st.write(f"Example: {cluster_texts[0][:100]}...")
    
    return by_category
```

---

### 10. Final Data Backup - Version Control
**Purpose**: Safety copy of Final Data sheet

**Reason**: Preserves data state before modifications/updates

---

### 10. Final Data Backup - Version Control
**Purpose**: Safety copy of Final Data sheet

**Structure**:
- **Dimensions**: 501 records × 21 columns (same row count as Final Data)
- **Differences**: Missing 8 columns compared to Final Data (29 vs 21 columns)
- **100% nulls** in "Flag (Green/Red)" column - suggests this was taken before flag assignment

**Reason**: Preserves data state before modifications/updates

#### Relevance to Our Application:

1. **Version Control Pattern**:
   - Shows real-world need for **data versioning**
   - Users manually created backup before making changes
   - System should automate this with proper version control

2. **Audit Trail Requirements**:
   - Compare "before" vs "after" states
   - Track what changed, when, and by whom
   - Roll back if changes were incorrect

3. **Change Detection**:
   - **Flag column**: All nulls in backup, populated in Final Data
   - Shows review process: blank → Green/Red/Not Considered
   - System can automatically detect and highlight changes

#### How We Can Use It:

```python
# 1. In src/db/postgres.py - Automatic versioning
CREATE TABLE gl_account_versions (
    version_id SERIAL PRIMARY KEY,
    gl_account_id INTEGER REFERENCES gl_accounts(id),
    version_number INTEGER NOT NULL,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    change_reason VARCHAR(255),
    data JSONB NOT NULL,  -- Full snapshot of account data
    UNIQUE(gl_account_id, version_number)
);

def create_version_snapshot(gl_account_id: int, user_id: int, reason: str):
    """Auto-create version before any update"""
    
    current = session.query(GLAccount).get(gl_account_id)
    
    # Get latest version number
    latest = session.query(GLAccountVersion).filter_by(
        gl_account_id=gl_account_id
    ).order_by(GLAccountVersion.version_number.desc()).first()
    
    new_version_number = (latest.version_number + 1) if latest else 1
    
    # Create snapshot
    snapshot = GLAccountVersion(
        gl_account_id=gl_account_id,
        version_number=new_version_number,
        created_by=user_id,
        change_reason=reason,
        data=current.to_dict()  # Serialize all fields to JSON
    )
    
    session.add(snapshot)
    session.commit()
    
    logger.info(f"Created version {new_version_number} for GL {current.account_code}")
    return snapshot

# 2. In src/app.py - Version history viewer
def render_version_history(gl_code: str):
    """Show change history for an account"""
    st.subheader(f"Version History - {gl_code}")
    
    account = session.query(GLAccount).filter_by(account_code=gl_code).first()
    versions = session.query(GLAccountVersion).filter_by(
        gl_account_id=account.id
    ).order_by(GLAccountVersion.version_number.desc()).all()
    
    for v in versions:
        with st.expander(f"Version {v.version_number} - {v.snapshot_date.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns(2)
            col1.write(f"**Changed by**: {v.created_by}")
            col2.write(f"**Reason**: {v.change_reason}")
            
            # Show diff if not first version
            if v.version_number > 1:
                prev_version = session.query(GLAccountVersion).filter_by(
                    gl_account_id=account.id,
                    version_number=v.version_number - 1
                ).first()
                
                diff = compare_versions(prev_version.data, v.data)
                st.write("**Changes:**")
                for field, (old_val, new_val) in diff.items():
                    st.write(f"- {field}: `{old_val}` → `{new_val}`")
            
            # Rollback option (admin only)
            if st.session_state.user_role == 'admin':
                if st.button(f"Rollback to v{v.version_number}", key=f"rollback_{v.version_id}"):
                    rollback_to_version(account.id, v.version_id)
                    st.success(f"Rolled back to version {v.version_number}")
                    st.rerun()

# 3. In src/data_validation.py - Compare backup vs current
def validate_data_changes(backup_df, current_df):
    """Detect and validate changes (like Final Data Backup vs Final Data)"""
    
    # Merge on account code
    merged = backup_df.merge(
        current_df,
        on='G/L Acct',
        suffixes=('_backup', '_current'),
        how='outer'
    )
    
    # Detect changes
    changes = []
    
    for _, row in merged.iterrows():
        gl_code = row['G/L Acct']
        
        # Check each column for changes
        for col in backup_df.columns:
            if col == 'G/L Acct':
                continue
            
            backup_val = row.get(f'{col}_backup')
            current_val = row.get(f'{col}_current')
            
            if pd.notna(backup_val) and pd.notna(current_val):
                if backup_val != current_val:
                    changes.append({
                        'gl_code': gl_code,
                        'field': col,
                        'old_value': backup_val,
                        'new_value': current_val
                    })
    
    # Analyze change patterns
    change_df = pd.DataFrame(changes)
    
    st.write(f"**Total changes detected**: {len(changes)}")
    st.write(f"**Accounts modified**: {change_df['gl_code'].nunique()}")
    st.write(f"**Fields changed**: {change_df['field'].unique()}")
    
    # Most common changes
    st.write("**Most frequently changed fields:**")
    st.dataframe(change_df['field'].value_counts())
    
    return change_df

# 4. In src/db/mongodb.py - Log all changes to audit trail
def log_data_change(gl_code: str, field: str, old_value, new_value, user_id: int, reason: str):
    """Log every change to MongoDB audit trail"""
    
    change_log = {
        'gl_code': gl_code,
        'field': field,
        'old_value': str(old_value),
        'new_value': str(new_value),
        'changed_by': user_id,
        'change_reason': reason,
        'timestamp': datetime.now(),
        'change_type': 'update',  # 'update', 'create', 'delete'
        'ip_address': get_client_ip(),  # For security audit
        'session_id': get_session_id()
    }
    
    get_audit_trail_collection().insert_one(change_log)
    
    # Also trigger version snapshot in PostgreSQL
    account = session.query(GLAccount).filter_by(account_code=gl_code).first()
    create_version_snapshot(account.id, user_id, reason)

# 5. In src/visualizations.py - Change timeline visualization
def create_change_timeline(period: str):
    """Visualize data changes over time"""
    import plotly.graph_objects as go
    
    # Get audit trail from MongoDB
    changes = get_audit_trail_collection().find({
        'timestamp': {'$gte': datetime.strptime(period, '%Y-%m')}
    }).sort('timestamp', 1)
    
    # Group by day
    daily_changes = {}
    for change in changes:
        date = change['timestamp'].date()
        daily_changes[date] = daily_changes.get(date, 0) + 1
    
    # Plot timeline
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(daily_changes.keys()),
        y=list(daily_changes.values()),
        mode='lines+markers',
        name='Changes per Day',
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Data Change Activity Timeline",
        xaxis_title="Date",
        yaxis_title="Number of Changes",
        hovermode='x unified'
    )
    
    return fig

# 6. Great Expectations validation - Detect unauthorized changes
def create_change_detection_suite():
    """Validate that changes follow business rules"""
    
    suite = context.add_expectation_suite(suite_name="change_validation")
    
    expectations = [
        # Critical fields should not change without approval
        "expect_column_values_to_not_change(
            column='account_code',
            message='Account codes are immutable'
        )",
        
        # Balance changes must have audit trail
        "expect_column_value_changes_to_be_logged(
            column='balance',
            audit_collection='audit_trail'
        )",
        
        # Review status can only progress (pending → reviewed → approved)
        "expect_column_values_to_follow_workflow(
            column='review_status',
            allowed_transitions={
                'pending': ['reviewed', 'flagged'],
                'reviewed': ['approved', 'flagged'],
                'flagged': ['reviewed'],
                'approved': []  # Terminal state
            }
        )"
    ]
    
    return suite
```

---

### 11. AGEL Sheet - Entity-Specific Data (Adani Green Energy Limited)
**Purpose**: Entity-specific trial balance data

**Structure**:
- **Dimensions**: 501 records × 11 columns
- **Entity**: Company Code 5110 (Adani Green Energy Limited)
- **Period**: Quarterly data (Balance Carryforward + Current Period activity)

**Key Columns**:
- **CoCd**: Company Code (5110 - all same)
- **G/L acct**: GL Account Number
- **Short Text**: Abbreviated account description
- **Crcy**: Currency (INR - all same)
- **BusA**: Business Area (100% nulls - not used)
- **Balance Carryforward**: Opening balance
- **Balance, prev.periods**: Previous period activity (all zeros)
- **Debit rept.period**: Debit transactions in current period
- **Credit report per.**: Credit transactions in current period
- **Accumulated balance**: Current closing balance
- **Lookup**: Reference to Final Data sheet GL codes (32.5% nulls for skipped accounts)

**Massive Transaction Scale**:
- Debit range: ₹0 to ₹230 billion
- Credit range: ₹0 to ₹230 billion
- Net balance range: -₹70 billion to +₹92 billion

**Significance**: 
- Demonstrates multi-entity structure
- Separate sheet per legal entity
- May contain entity-specific account codes or groupings

#### Relevance to Our Application:

1. **Multi-Entity Architecture** (CRITICAL REQUIREMENT):
   - System must handle **1,000+ Adani Group entities**
   - Each entity has own chart of accounts (5110 = AGEL)
   - Some GL codes shared, some entity-specific
   - Consolidated reporting across entities required

2. **Transaction-Level Detail**:
   - Shows **detailed activity**: Opening + Debits + Credits = Closing
   - Formula validation: `Balance Carryforward + Debit - Credit = Accumulated balance`
   - Great Expectations can validate this math for every account

3. **Currency Handling**:
   - All INR in this dataset (aligns with Observations sheet: "INR only")
   - But multi-entity group may have foreign currencies (USD, EUR, etc.)
   - Need currency conversion for consolidation

4. **Lookup Column Pattern**:
   - Maps entity accounts to master chart (Final Data)
   - 32.5% nulls = entity-specific accounts not in master
   - Agent should handle: "Why is GL 11100200 missing from AGEL?"

5. **Period-over-Period Analysis**:
   - **Balance Carryforward**: Enables trend analysis
   - Compare current accumulated balance vs carryforward
   - Variance analysis: Did account behave as expected?

#### How We Can Use It:

```python
# 1. In src/db/postgres.py - Multi-entity support
CREATE TABLE entities (
    id SERIAL PRIMARY KEY,
    company_code VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    parent_entity_id INTEGER REFERENCES entities(id),  -- For group structure
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Modify gl_accounts table
ALTER TABLE gl_accounts 
ADD COLUMN company_code VARCHAR(20) REFERENCES entities(company_code),
ADD COLUMN balance_carryforward DECIMAL(18, 2),
ADD COLUMN debit_period DECIMAL(18, 2),
ADD COLUMN credit_period DECIMAL(18, 2);

# Ensure unique constraint per entity
ALTER TABLE gl_accounts
DROP CONSTRAINT IF EXISTS gl_accounts_account_code_entity_period_key,
ADD CONSTRAINT gl_accounts_account_code_entity_period_key 
    UNIQUE(account_code, company_code, period);

# 2. In src/data_ingestion.py - Ingest entity-specific data
def ingest_entity_trial_balance(entity_code: str, period: str, file_path: str):
    """Load entity-specific trial balance (like AGEL sheet)"""
    
    df = pd.read_excel(file_path, sheet_name=entity_code)
    
    # Validate entity exists
    entity = session.query(Entity).filter_by(company_code=entity_code).first()
    if not entity:
        raise ValueError(f"Entity {entity_code} not found in master")
    
    for _, row in df.iterrows():
        gl_account = GLAccount(
            account_code=str(row['G/L acct']),
            account_name=row['Short Text'],
            entity=entity.company_name,
            company_code=entity_code,
            balance=row['Accumulated balance'],
            balance_carryforward=row['Balance Carryforward'],
            debit_period=row['Debit rept.period'],
            credit_period=row['Credit report per.'],
            period=period,
            bs_pl='BS' if row['G/L acct'] < 30000000 else 'PL'  # Heuristic
        )
        
        session.merge(gl_account)
    
    session.commit()
    logger.info(f"Ingested {len(df)} accounts for entity {entity_code}")

# 3. In src/data_validation.py - Validate transaction math
def validate_trial_balance_math(entity_code: str, period: str):
    """Ensure Opening + Debits - Credits = Closing"""
    
    accounts = session.query(GLAccount).filter_by(
        company_code=entity_code,
        period=period
    ).all()
    
    errors = []
    
    for acc in accounts:
        # Formula: Carryforward + Debit - Credit = Balance
        expected_balance = (
            acc.balance_carryforward + 
            acc.debit_period - 
            acc.credit_period
        )
        
        # Allow 1 rupee tolerance for rounding
        if abs(expected_balance - acc.balance) > 1.00:
            errors.append({
                'account_code': acc.account_code,
                'expected': expected_balance,
                'actual': acc.balance,
                'variance': expected_balance - acc.balance
            })
    
    if errors:
        logger.error(f"Found {len(errors)} math errors in {entity_code}")
        return errors
    
    logger.info(f"✅ Trial balance math validated for {entity_code}")
    return None

# 4. In src/analytics.py - Consolidated reporting
def generate_consolidated_trial_balance(period: str, entity_codes: List[str] = None):
    """Consolidate trial balances across multiple entities"""
    
    query = session.query(
        GLAccount.account_code,
        GLAccount.account_name,
        func.sum(GLAccount.balance).label('consolidated_balance'),
        func.count(GLAccount.company_code).label('entity_count')
    ).filter(GLAccount.period == period)
    
    if entity_codes:
        query = query.filter(GLAccount.company_code.in_(entity_codes))
    
    consolidated = query.group_by(
        GLAccount.account_code,
        GLAccount.account_name
    ).all()
    
    # Build DataFrame
    df = pd.DataFrame([{
        'GL Account': c.account_code,
        'Description': c.account_name,
        'Consolidated Balance': c.consolidated_balance,
        'Number of Entities': c.entity_count
    } for c in consolidated])
    
    # Sort by absolute balance (materiality)
    df['Abs Balance'] = df['Consolidated Balance'].abs()
    df = df.sort_values('Abs Balance', ascending=False)
    df = df.drop('Abs Balance', axis=1)
    
    return df

# 5. In src/app.py - Entity selector and drill-down
def render_entity_dashboard():
    """Multi-entity dashboard with drill-down"""
    st.header("Entity Analysis")
    
    # Entity selector (1000+ entities in production)
    entities = session.query(Entity).filter_by(is_active=True).all()
    
    selected_entities = st.multiselect(
        "Select Entities",
        options=[e.company_code for e in entities],
        default=[e.company_code for e in entities[:5]],  # Default to first 5
        format_func=lambda x: f"{x} - {get_entity_name(x)}"
    )
    
    # Consolidated metrics
    st.subheader("Consolidated View")
    consolidated_df = generate_consolidated_trial_balance(
        period='2022-06',
        entity_codes=selected_entities
    )
    
    # Display metrics
    total_assets = consolidated_df[consolidated_df['Consolidated Balance'] > 0]['Consolidated Balance'].sum()
    total_liabilities = abs(consolidated_df[consolidated_df['Consolidated Balance'] < 0]['Consolidated Balance'].sum())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Entities", len(selected_entities))
    col2.metric("Total Assets", f"₹{total_assets/1e9:.2f}B")
    col3.metric("Total Liabilities", f"₹{total_liabilities/1e9:.2f}B")
    
    # Entity-wise breakdown
    st.subheader("Entity-wise Breakdown")
    
    for entity_code in selected_entities:
        with st.expander(f"{entity_code} - {get_entity_name(entity_code)}"):
            entity_df = get_entity_trial_balance(entity_code, '2022-06')
            
            # Entity metrics
            ecol1, ecol2, ecol3 = st.columns(3)
            ecol1.metric("Accounts", len(entity_df))
            ecol2.metric("Total Debit", f"₹{entity_df['debit_period'].sum()/1e9:.2f}B")
            ecol3.metric("Total Credit", f"₹{entity_df['credit_period'].sum()/1e9:.2f}B")
            
            # Top 10 accounts by balance
            top_accounts = entity_df.nlargest(10, 'balance', keep='all')
            st.dataframe(top_accounts[['account_code', 'account_name', 'balance']])

# 6. In src/langchain_tools.py - Entity mapping tool
class EntityLookupTool(BaseTool):
    name = "lookup_entity_account"
    description = "Check if GL account exists in specific entity's chart of accounts"
    
    def _run(self, gl_code: str, entity_code: str) -> str:
        """
        Answer questions like: 'Does AGEL have GL account 11100200?'
        Uses Lookup column logic from AGEL sheet
        """
        account = session.query(GLAccount).filter_by(
            account_code=gl_code,
            company_code=entity_code
        ).first()
        
        if account:
            return f"Yes, {entity_code} has GL {gl_code} ({account.account_name}) with balance ₹{account.balance:,.2f}"
        else:
            # Check if it's in master but not entity
            master = session.query(MasterChartOfAccounts).filter_by(
                account_code=gl_code
            ).first()
            
            if master:
                return f"GL {gl_code} exists in master chart but not used by entity {entity_code}"
            else:
                return f"GL {gl_code} not found in master chart of accounts"

# 7. Great Expectations - Entity data validation
def create_entity_validation_suite():
    """Validate AGEL-style entity data"""
    
    suite = context.add_expectation_suite(suite_name="entity_trial_balance_validation")
    
    expectations = [
        # All records must have same company code
        "expect_column_values_to_be_unique(column='CoCd')",
        "expect_column_values_to_equal(column='CoCd', value=5110)",  # For AGEL
        
        # Currency must be consistent
        "expect_column_values_to_be_in_set(column='Crcy', value_set=['INR'])",
        
        # Math validation
        "expect_compound_columns_to_be_unique(column_list=['G/L acct', 'CoCd'])",
        
        # Balance formula
        "expect_column_pair_values_A_to_be_greater_than_B(
            column_A='Debit rept.period',
            column_B=0,
            or_equal=True
        )",
        
        # Accumulated balance = Carryforward + Debit - Credit
        "expect_multicolumn_sum_to_equal(
            column_list=['Balance Carryforward', 'Debit rept.period'],
            subtract_columns=['Credit report per.'],
            result_column='Accumulated balance',
            tolerance=1.00  # Allow 1 rupee rounding
        )"
    ]
    
    return suite
```

**Critical Implementation Note**:
The AGEL sheet pattern (501 accounts × 11 columns) repeated across **1,000+ entities** means:
- **501,000+ total account records** in production
- Need **performant querying**: Indexed by (company_code, account_code, period)
- Consider **partitioning** PostgreSQL table by company_code
- **Aggregation queries** must be optimized for consolidation

---

### 12. Final Data - Old - Historical Comparison
**Purpose**: Previous version/period data

**Use Cases**:
- Period-over-period comparison
- Variance analysis
- Trend tracking
- Audit trail

---

## Data Schema for Application Development

Based on analysis, the recommended schema for `gl_accounts` PostgreSQL table:

```sql
CREATE TABLE gl_accounts (
    id SERIAL PRIMARY KEY,
    account_code VARCHAR(50) NOT NULL,           -- 8-digit GL code
    account_name VARCHAR(255) NOT NULL,          -- GL Account Description
    entity VARCHAR(255) NOT NULL,                -- Entity name (default: ABEX, AGEL, etc.)
    balance DECIMAL(18, 2) NOT NULL,             -- Account balance
    period VARCHAR(20) NOT NULL,                 -- Period (e.g., '2022-06', 'Q1-2023')
    
    -- Classification
    bs_pl VARCHAR(10),                           -- 'BS' or 'PL'
    status VARCHAR(50),                          -- Assets, Liabilities, Income, Expense
    account_category VARCHAR(100),               -- Main Head grouping
    
    -- Review Metadata
    review_status VARCHAR(50) DEFAULT 'pending', -- pending, reviewed, flagged
    review_flag VARCHAR(20),                     -- Green, Red, Not Considered
    review_checkpoint VARCHAR(255),              -- Validation performed
    
    -- Supporting Documentation
    report_type VARCHAR(100),                    -- Inventory report, Fixed asset report, etc.
    analysis_required BOOLEAN DEFAULT FALSE,
    
    -- Assignment
    assigned_user_id INTEGER REFERENCES users(id),
    criticality VARCHAR(20),                     -- Critical, Medium, Low
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(account_code, entity, period)
);
```

---

## Key Observations for Development

### 1. Data Quality Issues
- **Missing Headers**: Many columns labeled "Unnamed" - need proper mapping
- **Null Values**: 26-33% nulls in critical fields - requires validation rules
- **Duplicate Columns**: GL Account appears twice (string and numeric)
- **Inconsistent Formats**: Some descriptions multiline, some single line

### 2. Review Workflow Indicators
- **Three-tier Status**:
  1. Green (Complete & Approved)
  2. Red (Issues/Pending)
  3. Not Considered (Out of Scope)
  
- **Checkpoint Tracking**: Each account has validation checkpoint description

### 3. Multi-Entity Support Required
- Separate sheets per entity (AGEL example)
- Entity column in data schema essential
- Consolidation across entities needed

### 4. Supporting Documentation Types
Identified report types needing storage/link functionality:
- Inventory reports
- Fixed asset reports  
- Working papers/schedules
- Bank Reconciliation Statements (BRS)
- Vendor reconciliations

### 5. Criticality-Based Prioritization
- Accounts classified by risk: Critical, Medium, Low
- Zero-balance accounts tracked separately (102 found)
- Suggests need for smart assignment algorithm

---

## Recommendations for Data Ingestion

### Phase 1: Clean Core Data
1. Map "Final Data" sheet columns properly
2. Create column mapping configuration
3. Handle null values with business rules
4. Standardize account code format (8 digits, zero-padded)

### Phase 2: Extract Metadata
1. Parse Summary sheet for account groupings
2. Extract criticality from Sheet2
3. Load observations as comments
4. Link supporting doc types to accounts

### Phase 3: Multi-Period Support
1. Ingest "Final Data - Old" as previous period
2. Enable period-over-period comparison
3. Track variances automatically

### Phase 4: Multi-Entity Expansion
1. Create entity master table
2. Parameterize entity in ingestion
3. Support consolidated views

---

## Cleaned CSV Data for Ingestion

**File**: `data/sample/trial_balance_cleaned.csv`

Successfully extracted and cleaned **501 GL accounts** from Final Data sheet:

### Data Statistics:
- **Total Accounts**: 501
- **Balance Sheet Accounts**: 338 (Assets: 210, Liabilities: 121, Equity: 7)
- **P&L Accounts**: 163 (Expense: 144, Income: 19)
- **Review Status**: 227 reviewed, 111 flagged, 163 skipped
- **Criticality**: 251 Critical, 174 Medium, 76 Low

### CSV Structure (19 columns):
```csv
entity,period,account_code,account_name,balance,bs_pl,status,account_category,sub_category,criticality,review_frequency,department,review_status,review_flag,report_type,analysis_required,review_checkpoint,reconciliation_type,variance_pct
ABEX,2022-06,11100200,Stock of Capital Inventory-Domestic,3531804.53,BS,Assets,Capital Work in Progress,CWIP,Critical,Monthly,R2R,flagged,Red,Inventory report,True,"Direct Assets not capitalised as per Group Guidelines, apart amount tallied with Inventory listing and ageing",Non Reconciliation GL,Not Applicable
ABEX,2022-06,11100400,Stock of Stores & Spares-Domestic,6102197.23,BS,Assets,Inventories,Inventories - Stores and Spares,Medium,Quarterly,R2R,reviewed,Green,Inventory report,True,"Amount tallied with Inventory listing and ageing",Non Reconciliation GL,Not Applicable
```

**Extraction Script**: `scripts/extract_trial_balance.py` - Automated Excel → CSV conversion with data cleaning

---

## Integration with Problem Statement

### Mapping to Core Capabilities:

1. **Data Ingestion & Consolidation** ✅
   - Excel sheets → CSV → PostgreSQL pipeline
   - Multiple entity support (AGEL sheet demonstrates)
   - Responsibility assignment (criticality-based)

2. **Automated Report Generation** ✅
   - Summary sheet structure shows required reports
   - Status tracking by category
   - Variance analysis (old vs current sheets)

3. **Validation & Compliance Checks** ✅
   - Review checkpoint column maps to validation rules
   - Green/Red flag system for pass/fail
   - Balance reconciliation (Debits = Credits validation)

4. **Continuous Learning Loop** ✅
   - Observations sheet provides feedback data
   - Historical data (Final Data - Old) for training
   - Reviewer comments for model improvement

5. **Agentic Behaviour** ✅
   - Report types indicate autonomous analysis types
   - Analysis Required flag shows agent decision points
   - Checkpoint descriptions provide context for insights

6. **Interactive Visualization** ✅
   - Summary dashboard structure as template
   - Criticality-based drill-down (Sheet2)
   - Entity-wise views (AGEL sheet)

---

## Summary: How All 12 Sheets Work Together

### Data Flow Diagram:

```
┌─────────────────────┐
│  Base File (2736)   │ ◄── Source of Truth: Complete Chart of Accounts
│  Master accounts    │
└──────────┬──────────┘
           │
           │ Apply filters (nature, balance, activity)
           ↓
┌─────────────────────┐
│ Final Data - Old    │ ◄── Historical Template (2718 accounts)
│ (2718 accounts)     │     With standardized queries per type
└──────────┬──────────┘
           │
           │ Further filtering + Current period data
           ↓
┌─────────────────────┐
│ Final Data (501)    │ ◄── ⭐ PRIMARY REVIEW DATASET
│ Current period      │     Full metadata for active review
└──────────┬──────────┘
           │
           ├───────────────────────────┬────────────────────────┐
           │                           │                        │
           ↓                           ↓                        ↓
┌──────────────────┐      ┌──────────────────┐    ┌──────────────────┐
│ Sheet3 (166)     │      │ Main (304)       │    │ AGEL (501)       │
│ Assignments      │      │ Work in Progress │    │ Entity-specific  │
│ Multi-stage      │      │ Batch review     │    │ Company 5110     │
└──────────────────┘      └──────────────────┘    └──────────────────┘
           │                           │                        │
           └───────────────────────────┴────────────────────────┘
                                       │
                                       ↓
                           ┌──────────────────┐
                           │ Observations     │
                           │ User feedback    │
                           │ Improvement ideas│
                           └──────────────────┘
                                       │
                                       ↓
                           ┌──────────────────┐
                           │ Summary          │
                           │ Dashboard view   │
                           │ Status rollup    │
                           └──────────────────┘
```

### Integration Strategy:

1. **Ingestion**: Base File → Filter to Final Data
2. **Assignment**: Final Data → Sheet3 (assignments) + Sheet4 (bulk)
3. **Review**: Main (work in progress) + AGEL (entity drill-down)
4. **Feedback**: Observations → System improvements
5. **Reporting**: Summary → Executive dashboard
6. **Versioning**: Final Data Backup → Audit trail
7. **Historical**: Final Data - Old → Trend analysis

### Critical Implementation Priorities:

#### Phase 1: Core Data Pipeline
- ✅ Ingest Final Data (501 accounts) - **PRIMARY FOCUS**
- ✅ Populate gl_accounts table
- ⏳ Load Sheet3 assignments to responsibility_matrix
- ⏳ Ingest AGEL entity data (multi-entity pattern)

#### Phase 2: Historical & Master Data
- ⏳ Load Base File to master_chart_of_accounts (2736 accounts)
- ⏳ Load Final Data - Old for historical comparison
- ⏳ Build account filtering logic (2736 → 501 pipeline)

#### Phase 3: Workflow & Feedback
- ⏳ Implement multi-stage workflow (P.S → R.S → F.S from Sheet3)
- ⏳ Build query type library from standardized queries
- ⏳ Create user feedback collection (Observations pattern)

#### Phase 4: Advanced Features
- ⏳ Period-over-period comparison
- ⏳ Consolidated multi-entity reporting
- ⏳ ML-based account reviewability prediction
- ⏳ Automated query type detection

---

## Next Steps

1. ✅ Create cleaned CSV sample from Final Data sheet
2. ✅ Test data ingestion pipeline with sample
3. ✅ Validate PostgreSQL schema matches data structure
4. ⏳ Create responsibility matrix CSV from Sheet3 data
5. ⏳ Build Great Expectations suite for validation rules
6. ⏳ Implement multi-entity support in data model (AGEL pattern)

---

**Document Version**: 2.0  
**Last Updated**: November 7, 2025  
**Author**: Project Aura Development Team

**Change Log**:
- v2.0: Added comprehensive relevance analysis and usage examples for all 12 sheets with code samples
- v1.0: Initial sheet-by-sheet structure analysis
