# swim-data-tool - Development Context

## Overview

**swim-data-tool** is a modern Python CLI tool for swim team record management. It provides a unified interface for collecting, processing, and analyzing swim data from USA Swimming and World Aquatics APIs.

**Current Version:** 0.0.1 (Initial framework)

**Status:** 🚧 Under active development - CLI framework complete, commands are stubs

---

## Project Architecture

### Technology Stack

- **Python:** 3.11+ (modern type hints, improved performance)
- **Package Manager:** `uv` (fast, modern alternative to pip)
- **CLI Framework:** `click` (command-line interface)
- **Terminal UI:** `rich` (beautiful output, tables, progress bars)
- **Data Processing:** `pandas` (CSV manipulation, data analysis)
- **HTTP:** `requests` (API calls)
- **HTML Parsing:** `beautifulsoup4` + `lxml` (web scraping)
- **Config:** `python-dotenv` (environment variables)
- **Testing:** `pytest` + `pytest-cov` (unit tests, coverage)
- **Linting:** `ruff` (fast Python linter)
- **Type Checking:** `mypy` (static type analysis)

### Project Structure

```
swim-data-tool/
├── pyproject.toml              # Project configuration (replaces setup.py)
├── VERSION                     # Semantic version (0.0.1)
├── README.md                   # User documentation
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT license
├── .gitignore                  # Git ignore patterns
│
├── src/
│   └── swim_data_tool/         # Main package (underscores)
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point for python -m swim_data_tool
│       ├── version.py          # Version information
│       ├── cli.py              # CLI framework and commands
│       ├── py.typed            # PEP 561 type hints marker
│       │
│       ├── api/                # API clients
│       │   └── __init__.py
│       │
│       ├── commands/           # CLI command implementations
│       │   ├── __init__.py
│       │   ├── init.py        # Team initialization (stub)
│       │   └── status.py      # Status and config commands (working)
│       │
│       ├── models/             # Data models
│       │   └── __init__.py
│       │
│       └── utils/              # Utility functions
│           └── __init__.py
│
├── templates/                  # Initialization templates (TODO)
├── tests/                      # Test suite
│   ├── __init__.py
│   └── conftest.py            # Pytest fixtures
│
├── docs/                       # Documentation (TODO)
├── examples/                   # Usage examples (TODO)
└── .venv/                      # Virtual environment (not committed)
```

---

## Current State (v0.0.1)

### ✅ Complete

1. **Project Setup**
   - Modern `src/` layout structure
   - `pyproject.toml` configuration (PEP 517/518 compliant)
   - `uv` virtual environment
   - Package installable with `uv pip install -e .`

2. **CLI Framework**
   - `click` command structure
   - `rich` terminal output
   - Version command (`--version`)
   - Help system (`--help`)

3. **Working Commands**
   - `swim-data-tool status` - Shows current configuration
   - `swim-data-tool config` - Displays .env file
   - Both check for `.env` and guide user to init if missing

4. **Placeholder Commands** (stubs with "Coming soon" messages)
   - `swim-data-tool init <team-name>`
   - `swim-data-tool import swimmers --src=<source>`
   - `swim-data-tool import swimmer <name>`
   - `swim-data-tool classify unattached`
   - `swim-data-tool generate records`

5. **Development Tools**
   - Test framework (pytest)
   - Linting configuration (ruff)
   - Type checking (mypy)
   - Basic .gitignore

### 🚧 TODO for v0.1.0

1. **Implement `init` command**
   - Search USA Swimming API for team
   - Discover team codes, SwimCloud ID, LSC
   - Create directory structure
   - Generate `.env` file from template
   - Generate `README.md`, `claude.md`, `.gitignore`
   - Create `.swim-data-tool-version` file

2. **Create templates/**
   - `.env.template` - Environment variables with placeholders
   - `.gitignore.template` - Standard ignore patterns
   - `README.md.template` - Club repository documentation
   - `claude.md.template` - AI assistant context for clubs
   - `directory_structure.json` - Data folder layout definition

3. **Implement import commands**
   - USA Swimming API client
   - World Aquatics scraper
   - Swimmer data collection
   - Meet results collection
   - Progress tracking and resumability

4. **Implement classify command**
   - Unattached swim classification logic
   - Probationary vs other categorization
   - Ford affiliation rules

5. **Implement generate command**
   - Record generation by course/age group/event
   - Top 10 lists
   - Annual summaries

6. **Testing**
   - Unit tests for all commands
   - API client tests (mocked)
   - CLI integration tests

---

## Development Workflow

### Setup

```bash
cd ~/swimming/swim-data-tool

# Activate virtual environment
source .venv/bin/activate

# Install in editable mode
uv pip install -e .

# Install dev dependencies (when needed)
uv pip install -e ".[dev]"
```

### Running the Tool

```bash
# Via entry point (after install)
swim-data-tool --help
swim-data-tool status

# Via module
python -m swim_data_tool --help

# Via uv (no activation needed)
uv run swim-data-tool --help
```

### Testing

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=swim_data_tool --cov-report=html

# Specific test file
uv run pytest tests/test_commands/test_status.py
```

### Code Quality

```bash
# Lint
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .

# Type check
uv run mypy src/

# Format check
uv run ruff format --check .
```

### Building

```bash
# Build distribution
uv build

# Result: dist/swim_data_tool-0.0.1-py3-none-any.whl
```

---

## Multi-Club Architecture

### Design Philosophy

**swim-data-tool** is designed to work with multiple swim clubs from a single installation.

**Separation of Concerns:**
- **Tools repo** (`~/swimming/swim-data-tool`): Shared Python package, CLI tool
- **Club repos** (e.g., `~/swimming/ford`, `~/swimming/swas`): Club-specific data only

**Club repos contain:**
- `.env` - Configuration (team codes, IDs, paths)
- `data/` - Raw, processed, and generated data
- `claude.md` - Club-specific context and workflows
- `README.md` - Club information
- `.swim-data-tool-version` - Tool version tracking

**Club repos do NOT contain:**
- Python scripts (use shared tool)
- Virtual environment (use shared .venv)
- Tool source code

### Usage Pattern

```bash
# Navigate to club directory
cd ~/swimming/ford

# Run tool (uses shared installation)
source ~/swimming/swim-data-tool/.venv/bin/activate
swim-data-tool status

# Or with alias (add to ~/.zshrc)
alias swim-data-tool="~/swimming/swim-data-tool/.venv/bin/swim-data-tool"
```

---

## Configuration (.env)

Each club has its own `.env` file (not committed to git):

```bash
# Club Information
CLUB_NAME="Tucson Ford Dealers Aquatics"
CLUB_ABBREVIATION="TFDA"
CLUB_NICKNAME="Ford"

# USA Swimming
USA_SWIMMING_TEAM_CODE="AZ FORD"
USA_SWIMMING_TEAM_NAMES="Tucson Ford Dealers Aquatics,TFDA,Ford Aquatics"

# SwimCloud
SWIMCLOUD_TEAM_ID="8136"

# LSC
LSC_CODE="AZ"
LSC_NAME="Arizona Swimming"

# Data Directories (relative to club repo root)
DATA_DIR="data"
RAW_DIR="data/raw"
PROCESSED_DIR="data/processed"
RECORDS_DIR="data/records"

# Public Records Repository (optional)
PUBLIC_REPO_URL="https://github.com/aaryno/tucson-ford-dealers-aquatics-records.git"
PUBLIC_REPO_LOCAL="/tmp/tucson-ford-dealers-aquatics-records"

# Collection Settings
START_YEAR="1998"
END_YEAR="2025"
COURSES="scy,lcm,scm"
COLLECT_INTERNATIONAL="true"

# Tool Version (auto-managed)
SWIM_DATA_TOOL_VERSION="0.0.1"
```

---

## Planned Commands (Full Spec)

### init

```bash
swim-data-tool init "Team Name"
```

**What it does:**
1. Searches USA Swimming database for team (interactive if multiple matches)
2. Discovers team code, SwimCloud ID, LSC
3. Creates directory structure (data/raw, data/processed, data/records, logs)
4. Generates `.env` from template with discovered values
5. Generates `README.md` from template
6. Generates `claude.md` from template with club-specific context
7. Copies `.gitignore` template
8. Creates `.swim-data-tool-version`

**Output:**
- Fully initialized club repository ready for data collection

### import swimmers

```bash
swim-data-tool import swimmers --src=usa-swimming [--start-date=YYYY-MM-DD] [--end-date=YYYY-MM-DD]
swim-data-tool import swimmers --src=world-aquatics [options]
```

**What it does:**
1. Reads team codes from `.env`
2. Queries USA Swimming API for all swimmers ever on team
3. Downloads individual career data for each swimmer
4. Saves to `data/raw/swimmers/<swimmer-name>.csv`
5. Tracks progress in log (resumable)
6. Shows progress bar with rich

### import swimmer

```bash
swim-data-tool import swimmer "Swimmer Name" [--full] [--start-date] [--end-date]
```

**What it does:**
1. Downloads career data for specific swimmer
2. By default: only club-affiliated swims
3. With `--full`: all swims in career (including other clubs)
4. Useful for updating specific swimmers

### classify unattached

```bash
swim-data-tool classify unattached
```

**What it does:**
1. Reads swimmer career data from `data/raw/swimmers/`
2. Identifies unattached swims
3. Classifies into:
   - **Probationary**: Swims before joining team (allowed in records)
   - **Other**: Unattached after joining (college, time trials, etc.)
4. Writes to `data/processed/unattached/probationary/` and `.../ford-unattached/`

### generate records

```bash
swim-data-tool generate records [--course=scy|lcm|scm|all]
swim-data-tool generate top10 [--course=scy|lcm|scm|all]
swim-data-tool generate annual-summary --season=2025
```

**What it does:**
1. Reads processed data
2. Generates markdown files for:
   - Team records (by age group, event, course)
   - Top 10 all-time lists
   - Annual season summaries
3. Saves to `data/records/`
4. Includes indicators for swim types (‡ † ◊)

### publish

```bash
swim-data-tool publish records [--dry-run]
```

**What it does:**
1. Reads PUBLIC_REPO_URL from `.env`
2. Clones public repo (if needed)
3. Copies records from `data/records/` to public repo
4. Commits with timestamp
5. Pushes to GitHub
6. `--dry-run`: shows what would be published

---

## Data Flow

```
USA Swimming API
      ↓
swim-data-tool import swimmers
      ↓
data/raw/swimmers/*.csv (individual career files)
      ↓
swim-data-tool classify unattached
      ↓
data/processed/unattached/{probationary,ford-unattached}/*.csv
      ↓
swim-data-tool generate records
      ↓
data/records/{scy,lcm}/records.md
      ↓
swim-data-tool publish records
      ↓
GitHub (public records repo)
```

---

## Related Projects

### ford (private analysis repo)

**Location:** `/Users/aaryn/ford`

**Contains:**
- All Ford team data (raw, processed, records)
- Configuration files
- Logs and reports

**Will migrate to:** `~/swimming/ford` (Phase 4 of migration)

### south-west-aquatic-sports (private analysis repo)

**Location:** `~/swimming/south-west-aquatic-sports`

**Status:** To be initialized with `swim-data-tool init`

### tucson-ford-dealers-aquatics-records (public repo)

**Location:** `https://github.com/aaryno/tucson-ford-dealers-aquatics-records.git`

**Contains:** Published team records (no raw data, no PII)

---

## Migration Plan

### Phase 1: Complete swim-data-tool ✅ DONE (v0.0.1 framework)

- ✅ Project structure
- ✅ CLI framework
- ✅ Basic commands
- 🚧 Implement remaining commands (v0.1.0)

### Phase 2: Setup SWAS

Use `swim-data-tool init` to initialize south-west-aquatic-sports

### Phase 3: Test with SWAS

Verify all commands work with SWAS data before touching Ford

### Phase 4: Migrate Ford

Only after SWAS works perfectly

---

## Version Strategy

**Semantic Versioning:** MAJOR.MINOR.PATCH

- **v0.0.1** (current): Initial CLI framework
- **v0.1.0** (next): Implement init command + templates
- **v0.2.0**: Implement import commands
- **v0.3.0**: Implement classify command
- **v0.4.0**: Implement generate command
- **v0.5.0**: Implement publish command
- **v1.0.0**: First stable release

**Version Tracking:**
- `VERSION` file in tools repo
- `.swim-data-tool-version` in each club repo
- Tool warns if versions don't match

---

## GitHub Repository

**URL:** https://github.com/aaryno/swim-data-tool (to be created)

**Status:** 🔒 PRIVATE (until PII verified removed)

**Will contain:**
- All source code
- Templates
- Documentation
- Tests
- Examples

**Will NOT contain:**
- Club data
- .env files
- PersonKeys or DOB

---

## Quick Reference

### Common Tasks

```bash
# Check current version
swim-data-tool --version

# Show status
swim-data-tool status

# View configuration
swim-data-tool config

# Initialize new club (when implemented)
swim-data-tool init "Club Name"

# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

### File Locations

- Source code: `src/swim_data_tool/`
- Tests: `tests/`
- Templates: `templates/` (to be created)
- Documentation: `docs/` (to be created)
- Virtual environment: `.venv/`

### Important Files

- `pyproject.toml` - Project configuration
- `VERSION` - Current version number
- `CHANGELOG.md` - Version history
- `README.md` - User documentation
- `claude.md` - This file (AI context)

---

## Development Guidelines

### Code Style

- Use type hints throughout
- Follow PEP 8 (enforced by ruff)
- Use `rich` for all terminal output
- Use `click` for CLI commands
- Keep commands in separate files in `commands/`

### Testing

- Write tests for all new features
- Maintain >80% code coverage
- Use pytest fixtures for reusable test data
- Mock external API calls

### Documentation

- Update CHANGELOG.md for all changes
- Keep README.md user-focused
- Document API in code docstrings
- Update this file (claude.md) for architecture changes

### Commits

- Use conventional commits format
- Clear, descriptive commit messages
- One logical change per commit

---

## Known Issues / TODO

### Current
- [ ] No templates yet (needed for init command)
- [ ] No API clients implemented
- [ ] No tests written yet
- [ ] Commands are stubs

### For v0.1.0
- [ ] Implement init command
- [ ] Create all templates
- [ ] Add tests for status/config commands
- [ ] Create comprehensive README

### Future
- [ ] API rate limiting handling
- [ ] Caching for API responses
- [ ] Data validation
- [ ] Error recovery
- [ ] Internationalization support

---

## Resources

### Documentation
- [uv Documentation](https://github.com/astral-sh/uv)
- [click Documentation](https://click.palletsprojects.com/)
- [rich Documentation](https://rich.readthedocs.io/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0517/)

### Related Files
- Migration plan: `/Users/aaryn/ford/SWIM_DATA_TOOL_STRUCTURE.md`
- Python structure guide: `/Users/aaryn/ford/PYTHON_PROJECT_STRUCTURE_2025.md`

---

## Contact

**Project Owner:** Aaryn Rosenberg

**Repository:** https://github.com/aaryno/swim-data-tool (private)

---

**Last Updated:** 2025-10-07
**Version:** 0.0.1
