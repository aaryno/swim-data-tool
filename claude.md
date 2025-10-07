# swim-data-tool - Development Context

## Overview

**swim-data-tool** is a modern Python CLI tool for swim team record management. It provides a unified interface for collecting, processing, and analyzing swim data from USA Swimming and World Aquatics APIs.

**Current Version:** 0.2.0

**Status:** ✅ Import commands implemented - Ready to download swimmer data!

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
├── pyproject.toml              # Project configuration (PEP 517/518)
├── VERSION                     # Semantic version (0.1.0)
├── README.md                   # User documentation
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT license
├── claude.md                   # This file - AI development context
├── .gitignore                  # Git ignore patterns
│
├── src/
│   └── swim_data_tool/         # Main package (underscores)
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point for python -m swim_data_tool
│       ├── version.py          # Version information (reads VERSION file)
│       ├── cli.py              # CLI framework and main command group
│       ├── py.typed            # PEP 561 type hints marker
│       │
│       ├── api/                # API clients
│       │   ├── __init__.py
│       │   └── usa_swimming.py # USA Swimming API client + TeamInfo model
│       │
│       ├── commands/           # CLI command implementations
│       │   ├── __init__.py
│       │   ├── init.py         # Team initialization (IMPLEMENTED)
│       │   └── status.py       # Status and config commands (working)
│       │
│       ├── models/             # Data models
│       │   └── __init__.py
│       │
│       └── utils/              # Utility functions
│           └── __init__.py
│
├── templates/                  # Initialization templates
│   ├── env.template            # Environment configuration template
│   ├── .gitignore.template     # Git ignore template for teams
│   ├── README.md.template      # Team README template
│   ├── claude.md.template      # Team AI context template
│   └── gitkeep.template        # Directory preservation template
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_api/               # API tests
│   │   └── __init__.py
│   ├── test_commands/          # Command tests
│   │   ├── __init__.py
│   │   └── test_init.py        # Init command tests (8 passing)
│   └── test_models/            # Model tests
│       └── __init__.py
│
├── artifacts/                  # AI-generated documentation and artifacts
│                               # (task lists, design docs, notes)
│
├── docs/                       # Project documentation (future)
├── examples/                   # Usage examples (future)
└── .venv/                      # Virtual environment (not committed)
```

---

## Current State (v0.2.0)

### ✅ Complete

1. **Project Setup**
   - Modern `src/` layout structure
   - `pyproject.toml` configuration (PEP 517/518 compliant)
   - `uv` virtual environment
   - Package installable with `uv pip install -e .`

2. **CLI Framework**
   - `click` command structure
   - `rich` terminal output with panels and prompts
   - Version command (`--version`)
   - Help system (`--help`)

3. **Working Commands**
   - ✅ **`swim-data-tool init <team-name>`** - Initialize new team repositories
     - Interactive prompts for team information
     - Creates complete directory structure
     - Generates all configuration files from templates
     - Automatic version tracking
   - ✅ `swim-data-tool status` - Shows current configuration
   - ✅ `swim-data-tool config` - Displays .env file
   - ✅ **`swim-data-tool import swimmer <person-key>`** - Download single swimmer
     - Downloads complete career data by PersonKey
     - Saves to data/raw/swimmers/
     - Configurable year range
   - ✅ **`swim-data-tool import swimmers --file=<csv>`** - Batch download
     - Reads CSV with PersonKeys and names
     - Progress bar with rich
     - Resumability (skips existing files)
     - Dry-run mode for testing

4. **Template System**
   - `env.template` - Environment variables with placeholders
   - `.gitignore.template` - Standard ignore patterns
   - `README.md.template` - Club repository documentation
   - `claude.md.template` - AI assistant context for clubs
   - `gitkeep.template` - Preserve empty directories

5. **USA Swimming API Client** (Production Ready)
   - Real Sisense/Elasticube API integration
   - `query_times_multi_year()` - efficient multi-year queries
   - `download_swimmer_career()` - complete swimmer history
   - `to_dataframe()` - convert API results to pandas
   - Optimized chunking strategy (1 call or 3 chunks)
   - TeamInfo dataclass model

6. **Testing & Quality**
   - Test framework (pytest + pytest-cov)
   - Tests for init command and templates
   - Linting configuration (ruff)
   - Type checking (mypy)
   - GitHub Actions CI/CD (tests, linting, type checking)
   - All tests passing

### ✅ DONE in v0.2.0

1. **Implemented import commands**
   - ✅ USA Swimming API client with Sisense integration
   - ✅ `import swimmer` command for single downloads
   - ✅ `import swimmers` command for batch downloads
   - ✅ Progress tracking with rich progress bars
   - ✅ Resumability (skips existing files)
   - ⏭️ World Aquatics scraper (deferred to later version)

### 🚧 TODO for v0.3.0

1. **Implement classify command**
   - Unattached swim classification logic
   - Probationary vs other categorization
   - Team affiliation rules

### 🚧 TODO for v0.4.0

1. **Implement generate command**
   - Record generation by course/age group/event
   - Top 10 lists
   - Annual summaries

### 🚧 TODO for v0.5.0

1. **Implement publish command**
   - Publish records to public repository
   - Git integration
   - Dry-run mode

---

## Documentation & Artifact Guidelines

### AI Assistant Rules

**⚠️ IMPORTANT: No markdown files in root without approval**

When working on swim-data-tool, AI assistants must follow these rules:

1. **Artifact Location**: All AI-generated documentation, task lists, design documents, and notes MUST go in `artifacts/`
2. **Root Directory Protection**: Do NOT create markdown files in the project root without explicit user approval
3. **Existing Files Only**: Only modify existing root-level files (README.md, CHANGELOG.md, claude.md) when necessary
4. **Naming Convention**: Use descriptive kebab-case names for artifacts (e.g., `task-list-v0.2.0.md`, `api-design-notes.md`)

### Artifact Types

Store in `artifacts/`:
- Task lists and TODO tracking
- Design documents and ADRs (Architecture Decision Records)
- Feature planning documents
- Implementation notes
- Migration plans
- Research and analysis documents

### Protected Files

Only modify these root files when needed:
- `README.md` - User-facing documentation
- `CHANGELOG.md` - Version history (update on releases)
- `claude.md` - AI development context (update on major changes)
- `VERSION` - Version number (update on releases)

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

### CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push and pull requests:

**Jobs:**
- **test**: Runs pytest with coverage on Python 3.11 and 3.12
- **lint**: Runs ruff linting and formatting checks
- **type-check**: Runs mypy type checking

**Triggers:** Push to main/develop branches, all pull requests

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

### Phase 1: Complete swim-data-tool core ✅ DONE (v0.1.0)

- ✅ Project structure
- ✅ CLI framework
- ✅ Init command with templates
- ✅ Status and config commands
- 🚧 Import commands (v0.2.0)
- 🚧 Classify command (v0.3.0)
- 🚧 Generate command (v0.4.0)
- 🚧 Publish command (v0.5.0)

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
- `VERSION` file in tools repo (currently 0.1.0)
- `.swim-data-tool-version` in each club repo (auto-created by init)
- Tool warns if versions don't match (future feature)

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
- Templates: `templates/`
- Artifacts: `artifacts/` (AI-generated docs, task lists, notes)
- Documentation: `docs/` (future permanent docs)
- Examples: `examples/` (future usage examples)
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

### Current (v0.1.0)
- [x] Templates created and working
- [x] Init command fully implemented
- [x] Tests for init command
- [x] Comprehensive README updated
- [ ] Add integration tests for full init workflow
- [ ] Add tests for status/config commands

### For v0.2.0
- [ ] Implement actual USA Swimming API integration
- [ ] Implement World Aquatics scraper
- [ ] Add import swimmers command
- [ ] Add import swimmer command
- [ ] Progress tracking and resumability
- [ ] Add more comprehensive tests

### Future
- [ ] API rate limiting handling
- [ ] Caching for API responses
- [ ] Data validation and error recovery
- [ ] Version compatibility checking
- [ ] Multi-language support for international teams

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
**Version:** 0.1.0
