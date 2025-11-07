# Data Storage Mapping - Trial Balance Sheets to Tri-Store

**Date**: November 7, 2025  
**Purpose**: Map all 12 Trial Balance Excel sheets to appropriate storage locations in the tri-store architecture

---

## Storage Mapping by Sheet

### 📊 **Sheet 1: Summary** (93 rows × 4 columns)
**Content**: High-level dashboard with GL account review status by category

**Storage Strategy**:
- **PostgreSQL** ❌ (Not stored - generated dynamically)
- **MongoDB** ❌ (Not stored - generated dynamically)
- **File System** ✅ `data/processed/dashboard_summary.parquet` (Cached aggregation)

**Rationale**: This is a derived view. Generate on-the-fly from PostgreSQL `gl_accounts` table grouped by category and review status. Cache in Parquet for performance.

**Query Pattern**:
```sql
SELECT 
    account_category AS "Main Head",
    review_status AS "Flag",
    COUNT(*) as "Count"
FROM gl_accounts
WHERE period = '2022-06'
GROUP BY account_category, review_status
ORDER BY account_category;
```

---

### 📊 **Sheet 2: Final Data** (501 rows × 29 columns) ⭐ **PRIMARY**
**Content**: Complete trial balance with all GL accounts and review metadata

**Storage Strategy**:
- **PostgreSQL** ✅ **PRIMARY** → `gl_accounts` table (with extended columns)
- **MongoDB** ✅ → Store flexible metadata in `gl_metadata` collection
- **File System** ✅ → `data/processed/final_data_2022-06.parquet` (Query cache)

**PostgreSQL Schema** (Extended):
```sql
CREATE TABLE gl_accounts (
    -- Core identification
    id SERIAL PRIMARY KEY,
    account_code VARCHAR(50) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    entity VARCHAR(255) NOT NULL DEFAULT 'ABEX',
    company_code VARCHAR(20) NOT NULL DEFAULT '5500',
    
    -- Financial data
    balance DECIMAL(18, 2) NOT NULL,
    balance_carryforward DECIMAL(18, 2),
    debit_period DECIMAL(18, 2),
    credit_period DECIMAL(18, 2),
    period VARCHAR(20) NOT NULL,
    
    -- Classification
    bs_pl VARCHAR(10),  -- 'BS' or 'PL'
    status VARCHAR(50),  -- Assets, Liabilities, Income, Expense, Equity
    account_category VARCHAR(100),  -- Main Head
    sub_category VARCHAR(100),  -- Sub head
    
    -- Review metadata
    review_status VARCHAR(50) DEFAULT 'pending',  -- pending, reviewed, flagged, skipped
    review_flag VARCHAR(20),  -- Green, Red, Not Considered
    review_checkpoint TEXT,
    criticality VARCHAR(20),  -- Critical, Medium, Low
    review_frequency VARCHAR(20),  -- Monthly, Quarterly, Half Yearly
    
    -- Supporting documentation
    report_type VARCHAR(100),  -- Inventory report, Fixed asset report, etc.
    analysis_required BOOLEAN DEFAULT FALSE,
    reconciliation_type VARCHAR(50),  -- Reconciliation GL, Non Reconciliation GL
    variance_pct VARCHAR(50),
    
    -- Assignment
    assigned_user_id INTEGER REFERENCES users(id),
    department VARCHAR(50),  -- R2R, TRM, O2C, B2P, IDT
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(account_code, company_code, period)
);

-- Indexes for performance
CREATE INDEX idx_gl_accounts_period ON gl_accounts(period);
CREATE INDEX idx_gl_accounts_entity ON gl_accounts(entity);
CREATE INDEX idx_gl_accounts_company ON gl_accounts(company_code);
CREATE INDEX idx_gl_accounts_status ON gl_accounts(review_status);
CREATE INDEX idx_gl_accounts_criticality ON gl_accounts(criticality);
CREATE INDEX idx_gl_accounts_department ON gl_accounts(department);
CREATE INDEX idx_gl_accounts_composite ON gl_accounts(company_code, period, review_status);
```

**MongoDB Collection** (Flexible metadata):
```javascript
// Collection: gl_metadata
{
  _id: ObjectId,
  gl_code: "11100200",
  company_code: "5500",
  period: "2022-06",
  
  // Multi-valued fields (arrays)
  maker_checker: {
    maker: ["Saurin Gandhi", "30016980"],
    checker: ["Vikrant Shah", "30021767"]
  },
  
  // Detailed queries (can be very long text)
  query_details: {
    query_type: "Classification of Inventory between Opex and Capex...",
    working_needed: "1. Inventory Ageing report\n2. Working for Inventory reclassification...",
    action_points: [
      "Old Non moving inventories lying",
      "Provision for Non Moving Inventories",
      "Direct assets capitalisation"
    ]
  },
  
  // Confirmation requirements
  confirmation_type: "Working / Documents based",  // or "Internal / External"
  
  // Custom fields per account type
  custom_attributes: {
    schedule_number: 6,
    nature: "Inventory",
    frequency_days: 30
  },
  
  created_at: ISODate,
  updated_at: ISODate
}
```

**Sample Data**: See `data/sample/trial_balance_cleaned.csv` (501 records already extracted)

---

### 📊 **Sheet 3: Sheet2** (11 rows × 5 columns)
**Content**: Risk pivot analysis - accounts by criticality and reviewer

**Storage Strategy**:
- **PostgreSQL** ❌ (Not stored - generated dynamically)
- **MongoDB** ❌ (Not stored - generated dynamically)  
- **File System** ✅ `data/processed/risk_pivot.parquet` (Cached)

**Rationale**: Derived from `gl_accounts` aggregation by criticality. Generate on-demand.

**Query Pattern**:
```sql
SELECT 
    criticality,
    COUNT(*) as total_accounts,
    COUNT(CASE WHEN balance = 0 THEN 1 END) as zero_balance_count
FROM gl_accounts
WHERE period = '2022-06'
GROUP BY criticality;
```

---

### 📊 **Sheet 4: Main** (304 rows × 22 columns)
**Content**: Working sheet - subset of Final Data with additional review columns

**Storage Strategy**:
- **MongoDB** ✅ **PRIMARY** → `review_sessions` collection
- **PostgreSQL** ❌ (Links via `review_log`)
- **File System** ✅ `data/processed/active_review_batch.parquet`

**MongoDB Collection**:
```javascript
// Collection: review_sessions
{
  _id: ObjectId,
  session_id: "SESSION_2022_06_BATCH_01",
  session_type: "batch",  // or "entity", "department", "category"
  
  // Session metadata
  created_by: "user_123",
  created_at: ISODate("2022-06-15"),
  status: "in_progress",  // or "completed", "abandoned"
  
  // Accounts in this batch
  gl_codes: ["11100200", "11100400", "11100410", ...],  // 304 accounts
  
  // Progress tracking
  accounts_total: 304,
  accounts_reviewed: 187,
  accounts_pending: 117,
  accounts_flagged: 23,
  
  // Working notes (per account)
  working_data: {
    "11100200": {
      interim_notes: "Need to verify inventory classification",
      temporary_calculations: {...},
      draft_status: "needs_clarification",
      last_updated: ISODate
    }
  },
  
  // Session completion
  completed_at: null,
  completion_notes: null
}
```

---

### 📊 **Sheet 5: Sheet3** (166 rows × 37 columns) ⭐ **ASSIGNMENT MASTER**
**Content**: Assignment tracking with multi-stage workflow, query types, reclassification data

**Storage Strategy**:
- **PostgreSQL** ✅ **PRIMARY** → `responsibility_matrix` table (extended)
- **MongoDB** ✅ → `assignment_details` collection (for flexible fields)
- **File System** ❌

**PostgreSQL Schema** (Extended):
```sql
CREATE TABLE responsibility_matrix (
    id SERIAL PRIMARY KEY,
    
    -- Assignment identification
    assignment_id VARCHAR(50) UNIQUE,  -- ID from Sheet3
    gl_code VARCHAR(50) NOT NULL,
    company_code VARCHAR(20) NOT NULL DEFAULT '5500',
    
    -- User assignment
    assigned_user_id INTEGER REFERENCES users(id),
    department VARCHAR(50),  -- R Department
    person_name VARCHAR(255),  -- R Person Name (email)
    
    -- Multi-stage workflow status
    prepare_status VARCHAR(20),  -- P.S: Pending, Complete
    review_status VARCHAR(20),  -- R.S: Pending, Complete
    final_status VARCHAR(20),  -- F.S: Pending, Complete
    form_filled BOOLEAN DEFAULT FALSE,  -- FF
    approved BOOLEAN DEFAULT FALSE,  -- Ok
    
    -- Severity & Priority
    severity VARCHAR(20),  -- Critical, Medium, Low
    
    -- Financial reconciliation data
    amount_lc DECIMAL(18, 2),  -- Amt Lc
    reconciled_amount_lc DECIMAL(18, 2),
    bs_reclassification_lc DECIMAL(18, 2),  -- BS Reclassification LC
    pl_impact_amt_lc DECIMAL(18, 2),  -- P&L Impact Amt LC
    overall_reconciliation_status VARCHAR(50),
    
    -- Query tracking
    query_type TEXT,  -- Long text field
    working_needed TEXT,  -- Long text field
    
    -- Comments
    preparer_comment TEXT,  -- P Comment
    reviewer_comment TEXT,  -- R Comment
    
    -- Metadata
    assignment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(gl_code, company_code, assignment_id)
);

-- Indexes
CREATE INDEX idx_responsibility_assignment ON responsibility_matrix(assignment_id);
CREATE INDEX idx_responsibility_gl ON responsibility_matrix(gl_code);
CREATE INDEX idx_responsibility_user ON responsibility_matrix(assigned_user_id);
CREATE INDEX idx_responsibility_status ON responsibility_matrix(prepare_status, review_status, final_status);
CREATE INDEX idx_responsibility_severity ON responsibility_matrix(severity);
```

**MongoDB Collection** (Additional flexible data):
```javascript
// Collection: assignment_details
{
  _id: ObjectId,
  assignment_id: "832",  // Maps to responsibility_matrix
  gl_code: "11100200",
  
  // Financial year and reporting
  fiscal_year: "FY22-23",
  reporting_date: ISODate("2022-06-30"),
  server: 903,
  vertical: "Ports & Logistics",
  
  // Extended BPC (Business Planning & Consolidation) data
  bpc_gl_account: "11100200_BPC",
  bpc_gl_account_name: "Inventory - BPC Mapped",
  category: "Current Assets",
  local_currency: "INR",
  
  // Full query details (can be very long)
  detailed_query: {
    primary_question: "Classification of Inventory between Opex and Capex",
    sub_questions: [
      "Old Non moving inventories lying and Provision for Non Moving Inventories, if any",
      "Direct assets not capitalised and parked in inventories"
    ],
    deliverables: [
      "Inventory Ageing report",
      "Working for Inventory reclassification",
      "NMI provision working"
    ]
  },
  
  created_at: ISODate,
  updated_at: ISODate
}
```

---

### 📊 **Sheet 6: Base File** (2736 rows × 13 columns)
**Content**: Master chart of accounts - complete account universe before filtering

**Storage Strategy**:
- **PostgreSQL** ✅ **PRIMARY** → `master_chart_of_accounts` table
- **MongoDB** ❌
- **File System** ✅ `data/processed/master_coa.parquet`

**PostgreSQL Schema**:
```sql
CREATE TABLE master_chart_of_accounts (
    id SERIAL PRIMARY KEY,
    
    -- Account identification
    account_code VARCHAR(50) NOT NULL UNIQUE,
    account_description VARCHAR(255),
    
    -- Hierarchy
    group_gl_account VARCHAR(50),  -- Parent account
    main_group VARCHAR(100),
    sub_group VARCHAR(100),
    
    -- Classification
    bs_pl VARCHAR(10),  -- BS or PL
    schedule_number INTEGER,  -- Financial statement schedule (0-35)
    
    -- Trial balance data (entity 5500)
    tb_5500 DECIMAL(18, 2),  -- Original trial balance
    reclassification_mar_18 DECIMAL(18, 2),  -- Historical adjustment
    derived_tb_5500 DECIMAL(18, 2),  -- Calculated: TB + Reclassification
    
    -- Reporting amounts
    bs_amount DECIMAL(18, 2),
    amt_v1 DECIMAL(18, 2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,  -- In current review set (Final Data)
    last_reviewed_period VARCHAR(20),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_master_coa_code ON master_chart_of_accounts(account_code);
CREATE INDEX idx_master_coa_group ON master_chart_of_accounts(group_gl_account);
CREATE INDEX idx_master_coa_schedule ON master_chart_of_accounts(schedule_number);
CREATE INDEX idx_master_coa_active ON master_chart_of_accounts(is_active);
```

**Data Validation Rule**:
```python
# Great Expectations check
expect_column_pair_sum_to_equal(
    column_A="tb_5500",
    column_B="reclassification_mar_18",
    sum_column="derived_tb_5500",
    tolerance=0.01
)
```

---

### 📊 **Sheet 7: Sheet1** (0 rows × 0 columns)
**Content**: Empty placeholder sheet

**Storage Strategy**:
- **PostgreSQL** ❌
- **MongoDB** ❌
- **File System** ❌

**Rationale**: Empty - no storage needed. May be used for user scratch pad in UI.

---

### 📊 **Sheet 8: Sheet4** (18 rows × 2 columns)
**Content**: Simple account-to-reviewer mapping (bulk assignment)

**Storage Strategy**:
- **PostgreSQL** ✅ → Loaded into `responsibility_matrix` table
- **MongoDB** ❌
- **File System** ❌

**Pattern**: Bulk insert with `assignment_type='bulk'`

---

### 📊 **Sheet 9: Observations** (37 rows × 13 columns)
**Content**: User feedback, system improvement suggestions, dashboard requirements

**Storage Strategy**:
- **MongoDB** ✅ **PRIMARY** → `user_feedback` collection
- **PostgreSQL** ❌
- **File System** ❌

**MongoDB Collection**:
```javascript
// Collection: user_feedback
{
  _id: ObjectId,
  
  // Feedback content
  observation: "Document currency to remove as base of analysis is INR only",
  category: "feature_request",  // or "bug", "enhancement", "process_improvement"
  
  // Context
  submitted_by: "reviewer_team",
  submitted_at: ISODate,
  related_module: "dashboard",  // or "filters", "attachments", "workflow"
  
  // Status tracking
  status: "new",  // "new", "reviewed", "in_progress", "implemented", "rejected"
  priority: null,  // Set by product team: "high", "medium", "low"
  assigned_to: null,
  
  // Implementation details
  implementation_notes: null,
  implemented_at: null,
  implementation_version: null,
  
  // Related to specific GL or feature
  related_gl_codes: [],
  related_features: ["dashboard_cards", "filters"],
  
  // Voting/consensus
  upvotes: 0,
  downvotes: 0,
  
  created_at: ISODate,
  updated_at: ISODate
}
```

---

### 📊 **Sheet 10: Final Data Backup** (501 rows × 21 columns)
**Content**: Backup copy of Final Data before modifications

**Storage Strategy**:
- **PostgreSQL** ✅ → `gl_account_versions` table (version control)
- **MongoDB** ❌
- **File System** ✅ `data/processed/backups/final_data_backup_2022-06.parquet`

**PostgreSQL Schema** (Version control):
```sql
CREATE TABLE gl_account_versions (
    version_id SERIAL PRIMARY KEY,
    
    -- Link to current account
    gl_account_id INTEGER REFERENCES gl_accounts(id),
    account_code VARCHAR(50) NOT NULL,
    
    -- Version tracking
    version_number INTEGER NOT NULL,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- User tracking
    created_by INTEGER REFERENCES users(id),
    change_reason VARCHAR(255),
    
    -- Full snapshot as JSON
    snapshot_data JSONB NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(gl_account_id, version_number)
);

-- Indexes
CREATE INDEX idx_versions_account ON gl_account_versions(gl_account_id);
CREATE INDEX idx_versions_date ON gl_account_versions(snapshot_date DESC);
CREATE INDEX idx_versions_user ON gl_account_versions(created_by);
```

**Trigger**: Auto-create version before any UPDATE on `gl_accounts`

---

### 📊 **Sheet 11: AGEL** (501 rows × 11 columns)
**Content**: Entity-specific trial balance (Company Code 5110 - Adani Green Energy Limited)

**Storage Strategy**:
- **PostgreSQL** ✅ **PRIMARY** → `gl_accounts` table (with company_code=5110)
- **MongoDB** ❌
- **File System** ✅ `data/processed/entity_5110_2022-06.parquet`

**Rationale**: Same schema as Final Data, differentiated by `company_code` column. Multi-entity support built into main table.

**Sample Record**:
```sql
INSERT INTO gl_accounts (
    account_code, account_name, entity, company_code,
    balance, balance_carryforward, debit_period, credit_period,
    period, bs_pl
) VALUES (
    '11100200', 'Stk of Cap Inv-Dom', 'AGEL', '5110',
    569284.58, 0.00, 47954780.00, 47839970.00,
    '2022-06', 'BS'
);
```

**Validation**: `balance = balance_carryforward + debit_period - credit_period` (±1 rupee tolerance)

---

### 📊 **Sheet 12: Final Data - Old** (2718 rows × 11 columns)
**Content**: Historical template with standardized query types and filtering rules

**Storage Strategy**:
- **PostgreSQL** ✅ → `account_master_template` table
- **MongoDB** ✅ → `query_library` collection (standardized queries)
- **File System** ✅ `data/processed/historical_template_old.parquet`

**PostgreSQL Schema**:
```sql
CREATE TABLE account_master_template (
    id SERIAL PRIMARY KEY,
    
    -- Account identification
    account_code VARCHAR(50) NOT NULL UNIQUE,
    account_description VARCHAR(255),
    
    -- Classification
    bs_pl VARCHAR(10),
    nature VARCHAR(100),  -- "Inventory - Not Consider", "TRM - Not Consider", etc.
    
    -- Ownership
    department VARCHAR(50),  -- R2R, TRM, IDT, O2C, B2P
    main_head VARCHAR(100),
    sub_head VARCHAR(100),
    
    -- Review requirements
    reconciliation_report_type VARCHAR(100),  -- Working, Confirmation, BU Score card
    is_automated BOOLEAN,  -- Automated vs Manual
    standard_query_type TEXT,  -- Pre-defined query for this account type
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,  -- Currently in review cycle
    filter_reason VARCHAR(100),  -- Why filtered: "Not Consider", "Zero Balance", etc.
    last_reviewed_period VARCHAR(20),
    
    -- Historical balance
    balance_historical DECIMAL(18, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_template_nature ON account_master_template(nature);
CREATE INDEX idx_template_dept ON account_master_template(department);
CREATE INDEX idx_template_active ON account_master_template(is_active);
```

**MongoDB Collection** (Query library):
```javascript
// Collection: query_library
{
  _id: ObjectId,
  
  // Account nature/type
  account_nature: "Inventory - Not Consider",
  account_category: "Inventories",
  department: "R2R",
  
  // Standardized queries
  standard_queries: [
    "Inventory reclass (O & M / Capex)",
    "Non moving inventory ageing",
    "Direct assets capitalisation"
  ],
  
  // Required deliverables
  required_documents: [
    "Inventory Ageing report",
    "Working for Inventory reclassification",
    "Direct Assets capitalisation certificate"
  ],
  
  // Review guidelines
  review_guidelines: "Ensure proper classification between operational and capital expenditure...",
  
  // Common issues
  common_issues: [
    "Direct assets not capitalised as per Group Guidelines",
    "Old non-moving inventory not provided for"
  ],
  
  // Automation potential
  can_automate: false,
  automation_notes: "Requires judgment on capex vs opex classification",
  
  // Usage stats
  times_used: 245,
  last_used: ISODate,
  
  created_at: ISODate,
  updated_at: ISODate
}
```

---

## Summary Table: All Sheets Mapped

| Sheet Name | Rows | PostgreSQL Table | MongoDB Collection | File System | Purpose |
|------------|------|------------------|-------------------|-------------|---------|
| **Summary** | 93 | ❌ (Generated) | ❌ (Generated) | ✅ Cached Parquet | Dashboard aggregation |
| **Final Data** ⭐ | 501 | ✅ `gl_accounts` | ✅ `gl_metadata` | ✅ Query cache | PRIMARY review dataset |
| **Sheet2** | 11 | ❌ (Generated) | ❌ (Generated) | ✅ Cached Parquet | Risk pivot |
| **Main** | 304 | ❌ (Links via review_log) | ✅ `review_sessions` | ✅ Active batch | Work in progress |
| **Sheet3** ⭐ | 166 | ✅ `responsibility_matrix` | ✅ `assignment_details` | ❌ | Assignment master |
| **Base File** | 2736 | ✅ `master_chart_of_accounts` | ❌ | ✅ Master COA | Complete universe |
| **Sheet1** | 0 | ❌ | ❌ | ❌ | Empty placeholder |
| **Sheet4** | 18 | ✅ `responsibility_matrix` | ❌ | ❌ | Bulk assignment |
| **Observations** | 37 | ❌ | ✅ `user_feedback` | ❌ | Product feedback |
| **Final Data Backup** | 501 | ✅ `gl_account_versions` | ❌ | ✅ Backup Parquet | Version control |
| **AGEL** | 501 | ✅ `gl_accounts` (5110) | ❌ | ✅ Entity cache | Multi-entity data |
| **Final Data - Old** | 2718 | ✅ `account_master_template` | ✅ `query_library` | ✅ Historical | Query templates |

---

## New PostgreSQL Tables Summary

1. ✅ **gl_accounts** - Extended with 19 new columns from Final Data
2. ✅ **responsibility_matrix** - Extended with 15 new columns from Sheet3
3. ✅ **master_chart_of_accounts** - New table for Base File (2736 accounts)
4. ✅ **gl_account_versions** - New table for version control
5. ✅ **account_master_template** - New table for historical template

## New MongoDB Collections Summary

1. ✅ **gl_metadata** - Flexible metadata for GL accounts
2. ✅ **assignment_details** - Extended assignment data from Sheet3
3. ✅ **review_sessions** - Batch review tracking (Main sheet)
4. ✅ **user_feedback** - Product improvements from Observations
5. ✅ **query_library** - Standardized queries from Final Data - Old

---

**Next Steps**:
1. ✅ Update PostgreSQL schema with extended tables
2. ✅ Create MongoDB collection initialization
3. ✅ Generate sample data for all tables
4. ✅ Create data ingestion scripts for each sheet type
5. ✅ Build validation rules for cross-store integrity

---

**Document Version**: 1.0  
**Last Updated**: November 7, 2025  
**Author**: Project Aura Development Team
