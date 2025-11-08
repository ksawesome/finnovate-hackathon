"""
Document Processor for RAG System.

Loads, chunks, and prepares documents for vector store ingestion.
"""

import hashlib
from datetime import datetime
from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """Process and chunk documents for vector store ingestion."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor.

        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks for context continuity
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        self.processed_hashes = set()

    def load_documentation(self, docs_dir: str = "docs/") -> list[Document]:
        """
        Load all documentation files from docs directory.

        Args:
            docs_dir: Path to documentation directory

        Returns:
            List of LangChain Document objects
        """
        docs_path = Path(docs_dir)
        documents = []

        if not docs_path.exists():
            print(f"Warning: Documentation directory {docs_dir} not found")
            return documents

        # Recursively find all markdown files
        markdown_files = list(docs_path.rglob("*.md"))
        print(f"Found {len(markdown_files)} markdown files in {docs_dir}")

        for md_file in markdown_files:
            try:
                with open(md_file, encoding="utf-8") as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Create document with metadata
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(md_file),
                        "doc_type": self._infer_doc_type(md_file),
                        "filename": md_file.name,
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )
                documents.append(doc)
                print(f"  ✅ Loaded: {md_file.name}")

            except Exception as e:
                print(f"  ❌ Error loading {md_file}: {e}")

        print(f"\nTotal documentation loaded: {len(documents)} files")
        return documents

    def load_accounting_knowledge(self) -> list[Document]:
        """
        Load accounting domain knowledge from curated sources.

        Returns:
            List of accounting concept documents
        """
        knowledge_base = [
            {
                "title": "General Ledger Account Definition",
                "content": """
                A General Ledger (GL) account is a record used in accounting to sort and store
                balance sheet and income statement transactions. Each GL account has:
                - Account Code: Unique identifier (e.g., 10010001, 20030001)
                - Account Name: Descriptive label (e.g., Cash & Cash Equivalents, Trade Payables)
                - Category: Assets, Liabilities, Revenue, Expenses, or Equity
                - Balance: Current financial amount (Debit or Credit)
                - Department: Organizational unit responsible
                - Entity: Business unit (AEML, APSEZ, APEL, etc.)

                GL accounts form the foundation of financial reporting and must be reviewed
                periodically for accuracy and completeness. In Project Aura, we track 501 active
                GL accounts across 1,000+ entities for the Adani Group.
                """,
            },
            {
                "title": "Trial Balance Concept",
                "content": """
                A Trial Balance is a bookkeeping worksheet showing all ledger account balances
                at a specific date. Key principles:
                - Must balance: Total Debits = Total Credits
                - Prepared at period end (monthly, quarterly, annually)
                - Used to detect errors before financial statement preparation
                - Contains: Account Code, Account Name, Debit Balance, Credit Balance

                If trial balance doesn't balance, there are errors requiring investigation.
                Project Aura validates trial balance data with Great Expectations to ensure
                the fundamental accounting equation holds: Assets = Liabilities + Equity.
                """,
            },
            {
                "title": "Variance Analysis Methodology",
                "content": """
                Variance Analysis compares actual financial results to budgets or prior periods:
                - Period-over-Period: Current vs Previous (e.g., March 2024 vs Feb 2024)
                - Budget vs Actual: Planned vs Realized performance
                - Key metrics: Absolute variance, Percentage variance, Cumulative variance

                Significant variances (>10% or >₹50,000) require explanation and may indicate:
                - Business growth or decline
                - Seasonal patterns
                - Operational changes
                - Errors or irregularities requiring correction

                Project Aura automatically flags major variances for review and uses ML
                to identify anomalous patterns that may require immediate attention.
                """,
            },
            {
                "title": "SLA and Review Process",
                "content": """
                Service Level Agreements (SLA) for GL account reviews:
                - Critical accounts: 2 business days
                - High priority: 5 business days
                - Medium priority: 10 business days
                - Low priority: 15 business days

                Review process:
                1. Assignment to reviewer based on department and workload
                2. Upload of supporting documentation (invoices, reconciliations)
                3. Review and validation by assigned user
                4. Approval or flagging for issues
                5. Documentation in audit trail

                Overdue reviews trigger escalation to department heads. Project Aura tracks
                SLA compliance and sends automated reminders to reviewers.
                """,
            },
            {
                "title": "Supporting Documentation Requirements",
                "content": """
                All GL account balances require supporting documentation:
                - Bank reconciliations for cash accounts
                - Ageing reports for receivables/payables
                - Fixed asset registers for PPE accounts
                - Invoices and contracts for revenue/expenses
                - Journal entry support for manual postings

                Documents must be:
                - Uploaded to system within SLA deadline
                - In accepted formats (PDF, Excel, images)
                - Clearly labeled with account code and period
                - Retained for audit purposes (7 years minimum)

                Project Aura stores supporting docs in MongoDB with metadata for
                quick retrieval during audits or reviews.
                """,
            },
            {
                "title": "Project Aura System Overview",
                "content": """
                Project Aura is an AI-powered GL account review assistant for Adani Group's
                1,000+ entity finance operations. It automates:

                - Data Ingestion: CSV → PostgreSQL → MongoDB → Parquet
                - Validation: Great Expectations suite ensuring data quality
                - ML Intelligence: 3 models (anomaly detection, priority ranking, attention classification)
                - Conversational AI: RAG-powered agent answering accounting questions
                - Automated Reports: PDF/CSV exports with visual analytics
                - Interactive Dashboards: 5 dashboards (Overview, Financial, Review, Quality, Risk)

                Tech Stack: Python 3.11, PostgreSQL, MongoDB, ChromaDB, LangChain, Streamlit
                Storage: Tri-store architecture (relational, document, vector)
                ML: scikit-learn with continual learning from user feedback
                """,
            },
            {
                "title": "Criticality Levels",
                "content": """
                GL accounts are classified by criticality to prioritize review efforts:

                - Critical (2 days SLA): Cash, investments, intercompany balances
                  Impact: High - affects liquidity and group consolidation

                - High (5 days SLA): Trade receivables, payables, revenue, COGS
                  Impact: Medium-High - affects P&L and working capital

                - Medium (10 days SLA): Prepaid expenses, accruals, provisions
                  Impact: Medium - affects accuracy but not immediate cash flow

                - Low (15 days SLA): Fixed assets, long-term liabilities
                  Impact: Low - stable balances with infrequent changes

                Project Aura assigns criticality automatically based on account category
                and historical review patterns.
                """,
            },
            {
                "title": "GL Hygiene Score",
                "content": """
                The GL Hygiene Score (0-100) measures financial data quality:

                Calculation:
                - Documentation completeness (30%): % of accounts with supporting docs
                - Review timeliness (25%): % of reviews completed within SLA
                - Balance accuracy (20%): % of accounts with no flags/adjustments
                - Data quality (15%): % passing validation rules
                - Process compliance (10%): % following standard review workflow

                Grading:
                - A (90-100): Excellent hygiene, minimal risk
                - B (80-89): Good hygiene, some improvements needed
                - C (70-79): Fair hygiene, moderate risk areas
                - D (60-69): Poor hygiene, significant issues
                - F (<60): Critical hygiene failure, immediate action required

                Target: All entities maintain B+ grade (≥85%) or higher.
                """,
            },
        ]

        documents = []
        for item in knowledge_base:
            doc = Document(
                page_content=f"# {item['title']}\n\n{item['content'].strip()}",
                metadata={
                    "source": "accounting_knowledge_base",
                    "doc_type": "accounting_knowledge",
                    "title": item["title"],
                    "created_at": datetime.utcnow().isoformat(),
                },
            )
            documents.append(doc)

        print(f"Loaded {len(documents)} accounting knowledge documents")
        return documents

    def load_gl_metadata(self) -> list[Document]:
        """
        Load GL account metadata as searchable documents.

        Returns:
            List of GL account description documents
        """
        try:
            from src.db import get_postgres_session
            from src.db.postgres import GLAccount
        except ModuleNotFoundError:
            # Handle standalone execution
            import sys
            from os.path import abspath, dirname

            sys.path.insert(0, dirname(dirname(abspath(__file__))))
            from db import get_postgres_session
            from db.postgres import GLAccount

        session = get_postgres_session()
        documents = []

        try:
            # Get all accounts (limit to 100 for vector store efficiency)
            accounts = session.query(GLAccount).limit(100).all()

            for account in accounts:
                content = f"""
Account Code: {account.account_code}
Account Name: {account.account_name}
Category: {account.account_category or 'Unknown'}
Department: {account.department or 'Unknown'}
Entity: {account.entity}
Period: {account.period}
Balance: ₹{account.balance:,.2f}
Status: {account.status or 'Unknown'}
Criticality: {account.criticality or 'Unknown'}
Review Status: {account.review_status or 'pending'}

This is a {account.account_category or 'general'} account managed by the {account.department or 'finance'} department.
Current balance is {'debit' if account.balance >= 0 else 'credit'} of ₹{abs(account.balance):,.2f}.
Entity: {account.entity}, Period: {account.period}
                """.strip()

                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "gl_accounts_metadata",
                        "doc_type": "metadata",
                        "account_code": account.account_code,
                        "category": account.account_category or "Unknown",
                        "entity": account.entity,
                        "period": account.period,
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )
                documents.append(doc)

            print(f"Loaded {len(documents)} GL account metadata documents")

        except Exception as e:
            print(f"Error loading GL metadata: {e}")

        finally:
            session.close()

        return documents

    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        """
        Split documents into chunks for vector store.

        Args:
            documents: List of Document objects

        Returns:
            List of chunked Document objects with metadata
        """
        chunked_docs = []
        total_chunks = 0

        for doc in documents:
            # Check if already processed (using content hash)
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
            if content_hash in self.processed_hashes:
                continue

            # Split document into chunks
            chunks = self.text_splitter.split_text(doc.page_content)
            total_chunks += len(chunks)

            # Create Document objects for each chunk
            for i, chunk_text in enumerate(chunks):
                chunk_doc = Document(
                    page_content=chunk_text,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "content_hash": content_hash,
                    },
                )
                chunked_docs.append(chunk_doc)

            self.processed_hashes.add(content_hash)

        print(f"\nChunked {len(documents)} documents into {total_chunks} chunks")
        return chunked_docs

    def process_all_documents(self, docs_dir: str = "docs/") -> dict[str, list[Document]]:
        """
        Load and process all document types.

        Args:
            docs_dir: Path to documentation directory

        Returns:
            Dict mapping document types to chunked documents
        """
        print("=" * 80)
        print("📚 Processing Documents for RAG System")
        print("=" * 80)

        # Load all document types
        print("\n1️⃣ Loading Documentation...")
        docs = self.load_documentation(docs_dir)

        print("\n2️⃣ Loading Accounting Knowledge...")
        accounting_docs = self.load_accounting_knowledge()

        print("\n3️⃣ Loading GL Metadata...")
        metadata_docs = self.load_gl_metadata()

        # Chunk all documents
        print("\n4️⃣ Chunking Documents...")
        all_docs = docs + accounting_docs + metadata_docs
        chunked = self.chunk_documents(all_docs)

        # Separate by type
        result = {
            "project_docs": [
                c
                for c in chunked
                if c.metadata["doc_type"]
                in ["documentation", "architecture", "adr", "guide", "implementation", "testing"]
            ],
            "gl_knowledge": [
                c for c in chunked if c.metadata["doc_type"] == "accounting_knowledge"
            ],
            "account_metadata": [c for c in chunked if c.metadata["doc_type"] == "metadata"],
        }

        print("\n" + "=" * 80)
        print("📊 Document Processing Summary")
        print("=" * 80)
        print(f"  Project Documentation: {len(result['project_docs'])} chunks")
        print(f"  Accounting Knowledge: {len(result['gl_knowledge'])} chunks")
        print(f"  GL Account Metadata: {len(result['account_metadata'])} chunks")
        print(f"  Total Chunks: {len(chunked)}")
        print("=" * 80)

        return result

    def _infer_doc_type(self, file_path: Path) -> str:
        """Infer document type from file path."""
        path_str = str(file_path).lower()

        if "adr" in path_str:
            return "adr"
        elif "architecture" in path_str:
            return "architecture"
        elif "guide" in path_str or "tutorial" in path_str:
            return "guide"
        elif "phase" in path_str or "implementation" in path_str:
            return "implementation"
        elif "test" in path_str:
            return "testing"
        else:
            return "documentation"


if __name__ == "__main__":
    # Test document processing
    processor = DocumentProcessor()
    result = processor.process_all_documents()

    print("\n✅ Document processing test complete!")
