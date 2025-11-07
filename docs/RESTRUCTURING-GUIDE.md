# Documentation & Scripts Restructuring Guide

**Date:** November 7, 2025  
**Status:** ✅ Complete  
**Impact:** All documentation and scripts reorganized for scalability

---

## 🎯 What Changed

The `docs/` and `scripts/` directories have been reorganized into logical subdirectories for better maintainability, discoverability, and scalability.

---

## 📁 New Structure

### Documentation (`docs/`)

**Before:**
```
docs/
├── Architecture.md
├── Storage-Architecture.md
├── Data-Storage-Mapping.md
├── Phase-0-Complete.md
├── Trial-Balance-Data-Analysis.md
├── Test-Plan.md
├── Day-0-Setup-Complete.md
├── 6-Day-Execution-Plan.md
├── Concept-Note.md
├── Plan.md
├── Problem Statement MD.md
├── Mapping of Plan to PS.md
└── adr/
    ├── ADR-001-unified-python-stack.md
    └── ADR-002-agent-with-structured-tools.md
```

**After:**
```
docs/
├── README.md (NEW - Navigation guide)
├── phases/                     # Phase completion reports
│   ├── Phase-0-Complete.md
│   ├── IMPLEMENTATION-SUMMARY.md
│   └── Phase-0-Completion-Status.md
├── architecture/               # System design
│   ├── Architecture.md
│   ├── Storage-Architecture.md
│   └── Data-Storage-Mapping.md
├── guides/                     # Developer guides
│   ├── Trial-Balance-Data-Analysis.md
│   ├── Test-Plan.md
│   └── Day-0-Setup-Complete.md
├── adr/                        # Architectural Decision Records
│   ├── ADR-001-unified-python-stack.md
│   └── ADR-002-agent-with-structured-tools.md
└── planning/                   # Project plans
    ├── 6-Day-Execution-Plan.md
    ├── Concept-Note.md
    ├── Plan.md
    ├── Problem Statement MD.md
    └── Mapping of Plan to PS.md
```

### Scripts (`scripts/`)

**Before:**
```
scripts/
├── bootstrap.ps1
├── local_db_setup.ps1
├── setup-postgres-local.ps1
├── setup-mongodb-local.ps1
├── cleanup-old-diagrams.ps1
├── render-diagrams.ps1
├── export-docs.ps1
├── init-postgres.sql
├── reset_database.py
├── seed_sample_data.py
├── extract_trial_balance.py
└── analyze_trial_balance.py
```

**After:**
```
scripts/
├── README.md (NEW - Usage guide)
├── setup/                      # Environment setup
│   ├── bootstrap.ps1
│   ├── local_db_setup.ps1
│   ├── setup-postgres-local.ps1
│   ├── setup-mongodb-local.ps1
│   ├── cleanup-old-diagrams.ps1
│   ├── render-diagrams.ps1
│   └── export-docs.ps1
├── database/                   # Database management
│   ├── init-postgres.sql
│   ├── reset_database.py
│   └── seed_sample_data.py
└── data/                       # Data extraction/analysis
    ├── extract_trial_balance.py
    └── analyze_trial_balance.py
```

---

## 🔄 Migration Guide

### For Developers

#### **If you have scripts that reference old paths:**

**Old Command:**
```powershell
.\scripts\bootstrap.ps1
python scripts\seed_sample_data.py
```

**New Command:**
```powershell
.\scripts\setup\bootstrap.ps1
python scripts\database\seed_sample_data.py
```

#### **If you have documentation links:**

**Old Link:**
```markdown
[Architecture](docs/Architecture.md)
```

**New Link:**
```markdown
[Architecture](docs/architecture/Architecture.md)
```

#### **Quick Find Reference:**

| Old Path | New Path | Category |
|----------|----------|----------|
| `docs/Architecture.md` | `docs/architecture/Architecture.md` | Architecture |
| `docs/Storage-Architecture.md` | `docs/architecture/Storage-Architecture.md` | Architecture |
| `docs/Data-Storage-Mapping.md` | `docs/architecture/Data-Storage-Mapping.md` | Architecture |
| `docs/Phase-0-Complete.md` | `docs/phases/Phase-0-Complete.md` | Phase Reports |
| `docs/Trial-Balance-Data-Analysis.md` | `docs/guides/Trial-Balance-Data-Analysis.md` | Guides |
| `docs/Test-Plan.md` | `docs/guides/Test-Plan.md` | Guides |
| `docs/Day-0-Setup-Complete.md` | `docs/guides/Day-0-Setup-Complete.md` | Guides |
| `docs/6-Day-Execution-Plan.md` | `docs/planning/6-Day-Execution-Plan.md` | Planning |
| `docs/Concept-Note.md` | `docs/planning/Concept-Note.md` | Planning |
| `scripts/bootstrap.ps1` | `scripts/setup/bootstrap.ps1` | Setup |
| `scripts/seed_sample_data.py` | `scripts/database/seed_sample_data.py` | Database |
| `scripts/extract_trial_balance.py` | `scripts/data/extract_trial_balance.py` | Data |

---

## 📝 Updated References

### In Code

If you have hardcoded paths in Python scripts, update them:

```python
# OLD
doc_path = "docs/Trial-Balance-Data-Analysis.md"
script_path = "scripts/seed_sample_data.py"

# NEW
doc_path = "docs/guides/Trial-Balance-Data-Analysis.md"
script_path = "scripts/database/seed_sample_data.py"
```

### In Copilot Instructions

The `.github/copilot-instructions.md` has been updated with the new structure:

```markdown
### Documentation Structure
docs/
├── phases/              # Phase completion reports
├── architecture/        # System design documents
├── guides/              # Developer guides and analysis
├── adr/                 # Architectural Decision Records
└── planning/            # Project plans
```

---

## 🎯 Benefits of New Structure

### 1. **Better Discoverability**
- Clear categories make finding documents easier
- README files provide navigation guidance
- Logical grouping reduces cognitive load

### 2. **Scalability**
- Easy to add new documents to appropriate categories
- No flat directory clutter
- Supports growth to 50+ documents

### 3. **Maintainability**
- Related documents grouped together
- Easier to update related docs
- Clear ownership by category

### 4. **CI/CD Integration**
- Can run different checks per directory
- Phase reports can trigger different workflows
- Documentation validation by category

---

## 📚 New README Files

### `docs/README.md`
- **Purpose:** Navigation guide for all documentation
- **Features:**
  - Quick reference table ("When to Read What")
  - Document categories explanation
  - Best practices for documentation
  - Document status tracker
- **Usage:** Start here when looking for any documentation

### `scripts/README.md`
- **Purpose:** Usage guide for all automation scripts
- **Features:**
  - Quick start commands
  - Script-by-script documentation
  - Common workflows
  - Troubleshooting guide
- **Usage:** Reference before running any script

---

## ✅ Verification

### Check New Structure
```powershell
# Verify docs structure
Get-ChildItem -Path docs -Directory
# Expected: adr, architecture, guides, phases, planning

# Verify scripts structure
Get-ChildItem -Path scripts -Directory
# Expected: data, database, setup

# Check README files exist
Test-Path docs\README.md, scripts\README.md
# Expected: True, True
```

### Verify Script Paths
```powershell
# Test new script paths
python scripts\database\seed_sample_data.py
.\scripts\setup\bootstrap.ps1
python scripts\data\extract_trial_balance.py
```

### Verify Documentation Links
```powershell
# Check if documents moved correctly
Test-Path docs\architecture\Architecture.md
Test-Path docs\phases\Phase-0-Complete.md
Test-Path docs\guides\Trial-Balance-Data-Analysis.md
# All should return True
```

---

## 🔧 Updating Your Workflows

### If you have automation scripts:

```powershell
# OLD workflow
.\scripts\local_db_setup.ps1
python scripts\seed_sample_data.py

# NEW workflow
.\scripts\setup\local_db_setup.ps1
python scripts\database\seed_sample_data.py
```

### If you have documentation generators:

Update path references in tools that generate or link documentation:

```python
# Example: Update documentation links
old_links = {
    "docs/Architecture.md": "docs/architecture/Architecture.md",
    "docs/Phase-0-Complete.md": "docs/phases/Phase-0-Complete.md",
    # ... add all mappings
}

for old, new in old_links.items():
    content = content.replace(f"]({old})", f"]({new})")
```

---

## 📞 Need Help?

### Common Questions

**Q: Where did [file].md go?**  
A: Check the migration table above or search:
```powershell
Get-ChildItem -Path docs -Recurse -Filter "[file].md"
```

**Q: My script path broke, what's the new path?**  
A: Check `scripts/README.md` for the script you need, or search:
```powershell
Get-ChildItem -Path scripts -Recurse -Filter "[script].py"
```

**Q: How do I know which category to use for a new document?**  
A: Read `docs/README.md` section "Document Categories" for guidelines

**Q: Can I still use old paths temporarily?**  
A: No, files have been moved. Update your scripts to use new paths.

---

## 🎓 Best Practices Going Forward

### For New Documents

1. **Choose the right category:**
   - Phases: Completion reports with metrics
   - Architecture: System design and technical decisions
   - Guides: How-to documents and analysis
   - Planning: Business context and roadmaps
   - ADR: Architectural decision records

2. **Update README:**
   - Add new document to `docs/README.md`
   - Include purpose, when to read, and key features

3. **Cross-reference:**
   - Use relative paths: `../architecture/Architecture.md`
   - Update related documents with links

### For New Scripts

1. **Choose the right category:**
   - Setup: Environment and infrastructure
   - Database: Schema and data management
   - Data: Extraction, transformation, analysis

2. **Update README:**
   - Add script to `scripts/README.md`
   - Document purpose, usage, prerequisites

3. **Follow naming conventions:**
   - Use snake_case for Python: `reset_database.py`
   - Use kebab-case for PowerShell: `setup-postgres-local.ps1`

---

**Migration Completed:** November 7, 2025  
**Files Reorganized:** 25+ files  
**New READMEs Created:** 2  
**Status:** ✅ Ready for use
