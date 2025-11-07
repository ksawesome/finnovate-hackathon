### **AURA: A Direct Response to the Problem Statement**

AURA is the definitive blueprint for building a prototype that directly addresses the core business problem: the time-consuming, manual, and repetitive nature of the financial statement review process at the Adani Group.[1] The entire plan is structured to build the exact "autonomous review agent" envisioned in the challenge.[1]

---

### **Mapping AURA to the Six Core Capabilities**

The problem statement specifies six core capabilities the AI agent must possess.[1] The AURA roadmap is designed to deliver each one in a logical, phased approach.

**1. Data Ingestion & Consolidation**
*   **Problem Statement Requirement:** The agent must collect data from spreadsheets, assign user responsibilities from a master matrix, handle manual uploads for non-SAP entities, and manage an automated email workflow for the review process.[1]
*   **AURA's Solution:**
    *   **Phase 1: Foundation & Data Pipeline** is entirely dedicated to this. The plan uses **Pandas** to ingest the `trial_balance.csv` and `responsibility_matrix.csv` files, directly implementing the required data consolidation.[1]
    *   The **Streamlit** UI, built in the same phase, provides the file uploader which serves as the mechanism for "manual trial report uploading".[1]
    *   The plan makes a strategic hackathon decision to **simulate the automated email workflow** with clear status updates in the UI. This acknowledges the requirement while freeing up critical development time for the high-impact AI features that are more crucial for a winning prototype.[1]

**2. Automated Report Generation**
*   **Problem Statement Requirement:** The agent must generate reports on the status of GL accounts, major variances compared to the previous period, and a graphical presentation of GL hygiene, using both tables and charts.[1]
*   **AURA's Solution:**
    *   **Phase 2: Validation & Automated Reporting** directly addresses this. The roadmap includes tasks to develop backend functions for "variance analysis" and "review status tracking."
    *   The technology stack specifies using **Streamlit** with **Plotly** to create the required interactive dashboard, including bar charts for variances and pie charts for review status, fulfilling the "tabular and visual summaries" requirement precisely.[1]

**3. Validation & Compliance Checks**
*   **Problem Statement Requirement:** The agent must perform critical data quality checks, most importantly ensuring that the "total of trial report is Nil" (i.e., debits equal credits).[1]
*   **AURA's Solution:**
    *   The plan incorporates a professional-grade solution by selecting **Great Expectations (GX)**.[2, 3] **Phase 2** includes the specific task of creating a GX "Expectation Suite" to programmatically validate that the sum of the debit column equals the sum of the credit column. This demonstrates a mature, "unit tests for data" approach that directly satisfies this key compliance check.[4, 1]

**4. Continuous Learning Loop**
*   **Problem Statement Requirement:** The agent must improve its accuracy with human feedback, using the example of a user correcting a line item, which the model then learns for the future.[1]
*   **AURA's Solution:**
    *   This is a central feature of **Phase 3: The Intelligence Layer**. The plan details a tangible user journey where a user corrects a misclassified GL account in the UI. This action triggers the backend to retrain a **Scikit-learn** classification model, creating a demonstrable, closed-loop system that provides clear "evidence of learning from user corrections".[5, 6, 1]

**5. Agentic Behaviour**
*   **Problem Statement Requirement:** The agent should function like a "reporting assistant," autonomously compiling data and proactively surfacing insights, such as, "Expense for the current period is X times the expenses of previous month".[1]
*   **AURA's Solution:**
    *   The selection of **LangChain** in the technology stack is specifically for this purpose.[7, 8] **Phase 3** focuses on structuring the backend functions as "Tools" that a LangChain agent can orchestrate.
    *   **Phase 4** then implements the "proactive insight" feature by having the agent display a contextually relevant summary on the main dashboard, directly mirroring the example in the problem statement.[1]

**6. Interactive Visualization**
*   **Problem Statement Requirement:** The solution must feature a dashboard with drill-down capabilities and a conversational interface to query reports with natural language (e.g., "Show me year-over-year Profit of Adani Ports").[1]
*   **AURA's Solution:**
    *   **Phase 4: UI & Conversational Interface** is dedicated to building this exact experience. The plan specifies using **Streamlit** to create a polished dashboard with drill-down functionality on charts.[9, 10]
    *   Crucially, it details the implementation of a chat interface (`st.chat_input`) that connects directly to the LangChain agent, allowing a manager to ask natural language questions and receive data-driven answers, precisely as requested in the problem statement.[1]

---

### **Mapping AURA to the Expected Hackathon Output**

The problem statement concludes with four clear deliverables for the prototype.[1] The AURA roadmap is scoped to deliver on all four points.

| Expected Output from Problem Statement [1] | How AURA Delivers This |
| :--- | :--- |
| **1. Upload or connect to sample datasets (CSV/Excel).** | **Phase 1** of the roadmap implements a Streamlit file uploader for exactly this purpose. |
| **2. AI Agent ingests, consolidates, and generates draft reports.** | The entire workflow across **Phases 1, 2, and 3** is designed to demonstrate this end-to-end process, from data ingestion with Pandas to report generation via the LangChain agent. |
| **3. Dashboard or conversational interface presents key numbers, charts, and anomalies.** | **Phase 4** focuses entirely on building this user interface with Streamlit, including the dashboard, charts for anomalies (variances), and the conversational chatbot. |
| **4. Evidence of learning from user corrections.** | The **Phase 3** implementation of the Scikit-learn model, which retrains based on user input from the UI, provides tangible and demonstrable evidence of this learning loop. |

In summary, the **AURA** plan is a direct, comprehensive, and strategic blueprint for building a winning prototype that meets every technical requirement and deliverable outlined in the original problem statement.

---

### Detailed Sub-Requirement Mapping to Plan Phases

This section maps every sub-requirement from the Problem Statement to AURA phases, concrete artifacts, and where applicable, the 6-Day plan days.

1) Data Ingestion & Consolidation

* Extract company-wise trial report from multiple SAP servers (daily)
    * Hackathon approach: Simulated via CSV uploads
    * Phase: Phase 1 (Foundation & Data Pipeline)
    * Artifacts: `app.py` uploaders; `src/data_ingestion.py` (load functions)
    * 6-Day: Day 1

* Assign responsibility (Name, Department, Email) to each GL based on master matrix
    * Phase: Phase 1
    * Artifacts: `consolidate_data()` join on GL_Account; consolidated DataFrame
    * 6-Day: Day 1

* NON-SAP entities: input template for manual trial report upload
    * Phase: Phase 1
    * Artifacts: Sample templates under `data/sample/`; uploader accepts same schema
    * 6-Day: Day 1

* Auto e-mail to each user for uploading the supporting document against each GL
    * Hackathon approach: Simulate via UI “Upload Supporting” status and reminders (no SMTP)
    * Phase: Phase 4 (UI & Conversational Interface)
    * Artifacts: Streamlit status badges, reminders panel, per-GL “Supporting Pending/Uploaded” flags
    * 6-Day: Day 4–5

* Auto e-mail to reviewer post the supporting/back-up working file uploaded by users
    * Hackathon approach: Simulate via UI “Notify Reviewer” action and status change
    * Phase: Phase 4
    * Artifacts: Status transition: Pending → Submitted → Under Review
    * 6-Day: Day 4–5

* Auto e-mail to Business FC post the GL account reviewed by the reviewer
    * Hackathon approach: Simulate via UI “Notify Business FC” with badge update
    * Phase: Phase 4
    * Artifacts: Status transition: Under Review → Reviewed (Reviewer) → FC Review Pending
    * 6-Day: Day 4–5

* Auto e-mail to each user post the GL account reviewed by Business FC
    * Hackathon approach: Simulate via UI final “Reviewed (FC)” badge and history log entry
    * Phase: Phase 4
    * Artifacts: Status transition: FC Review Pending → Reviewed (FC); activity log entry
    * 6-Day: Day 4–5

2) Automated Report Generation

* Exhaustive reports – pending supporting uploads
    * Phase: Phase 2 (Validation & Automated Reporting)
    * Artifacts: `get_review_status()`; Streamlit table and pie chart
    * 6-Day: Day 2

* Reviewed vs pending by stakeholder; counts
    * Phase: Phase 2
    * Artifacts: `get_review_status()` grouped by Person/Dept
    * 6-Day: Day 2

* Deviation vs assigned timelines (SLA)
    * Phase: Phase 2
    * Artifacts: SLA fields in status summary; badge coloring for overdue
    * 6-Day: Day 2–3

* Graphical presentation of GL hygiene (overall)
    * Phase: Phase 2
    * Artifacts: `create_hygiene_indicator()` gauge chart
    * 6-Day: Day 3

* Major GL variances vs last month/quarter
    * Phase: Phase 2
    * Artifacts: `calculate_variance()`; Plotly bar chart
    * 6-Day: Day 2–3

* Produce both tabular and visual summaries; special user queries
    * Phase: Phase 2 → visuals; Phase 4 → chat queries
    * Artifacts: Streamlit tables/charts; Agent query router
    * 6-Day: Day 3–4

3) Validation & Compliance Checks

* Role hierarchy/authorization (only relevant person can login)
    * Hackathon approach: Role-based demo personas; non-blocking for core demo
    * Phase: Phase 4
    * Artifacts: Simple role switch or pre-set personas in UI
    * 6-Day: Day 4–5

* Maker & checker matrix adherence
    * Hackathon approach: Simulate via personas and enforced status transitions (Maker → Reviewer → FC)
    * Phase: Phase 4 (UI flow), Phase 2 (data checks tied to statuses)
    * Artifacts: Status machine enforces sequence; activity log for auditability
    * 6-Day: Day 4–5

* Ensure total of trial report is Nil (Debits = Credits)
    * Phase: Phase 2
    * Artifacts: GX Expectation Suite; validation checkpoint; PASS/FAIL in UI
    * 6-Day: Day 2

* Working/supporting file values match GL account
    * Phase: Phase 2
    * Artifacts: Cross-checks in `analytics.py` and GX expectations where feasible
    * 6-Day: Day 2–3

* Post-extraction/post-review change in GL balance must be highlighted to User & Reviewer immediately
    * Phase: Phase 2 (detection) + Phase 4 (notification)
    * Artifacts: Delta detection logic; UI alerts/badges
    * 6-Day: Day 3–4

4) Continuous Learning Loop

* Learn common reporting errors/mismatches
    * Phase: Phase 3 (Intelligence Layer)
    * Artifacts: `src/ml_model.py` baseline model; `src/feedback_handler.py` feedback store
    * 6-Day: Day 3

* Improve accuracy with human feedback (“This line item is new”) → model learns correction
    * Phase: Phase 3
    * Artifacts: `retrain_model(...)` pipeline; UI correction flow
    * 6-Day: Day 3

5) Agentic Behaviour

* Work like a reporting assistant: autonomously collect, compile, draft, summarize
    * Phase: Phase 3 (tools) → Phase 4 (agent orchestration)
    * Artifacts: `src/langchain_tools.py`; `src/agent.py` initialize/execute agent
    * 6-Day: Day 3–4

* Proactively surface insights (e.g., current-period expense spike)
    * Phase: Phase 4
    * Artifacts: `src/insights.py`; insights displayed on dashboard
    * 6-Day: Day 4

6) Interactive Visualization

* Drill-down dashboards (profit/assets by BU; company-wise views)
    * Phase: Phase 4
    * Artifacts: `src/visualizations.py`; Plotly interactivity/drill-down handlers
    * 6-Day: Day 3–4

* Conversational interface to query reports (e.g., “Show me year-over-year Profit of Adani Ports”)
    * Phase: Phase 4
    * Artifacts: Streamlit chat UI; agent query router
    * 6-Day: Day 4

---

### Phase Coverage Matrix (Capabilities × Phases)

| Capability | P1: Data | P2: Validation & Reports | P3: Learning | P4: UI & Chat/Agent | P5: Integration & Pitch |
|---|:---:|:---:|:---:|:---:|:---:|
| 1) Ingestion & Consolidation | ✓ |  |  | ✓ (status UX) | ✓ (demo wiring) |
| 2) Automated Reports |  | ✓ |  | ✓ | ✓ |
| 3) Validation & Compliance |  | ✓ |  | ✓ (alerts/roles) | ✓ |
| 4) Continuous Learning |  |  | ✓ |  | ✓ |
| 5) Agentic Behaviour |  |  | ✓ (tools) | ✓ (agent) | ✓ |
| 6) Interactive Visualization |  |  |  | ✓ | ✓ |

Notes:
- Email workflow and ERP extraction are simulated for the hackathon via UI statuses and CSV uploads, respectively.
- Phase 5 is non-functional polish, integration, and pitch readiness; it consolidates prior phases for a stable demo.