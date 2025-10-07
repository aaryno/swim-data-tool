# swim-data-tool - Development Context

## Overview

**swim-data-tool** is a modern Python CLI tool for swim team record management. It provides a unified interface for collecting, processing, and analyzing swim data from USA Swimming and World Aquatics APIs.

**Current Version:** 0.4.2

**Status:** ✅ Production-ready for core workflow - init, roster, import, classify, generate all working!

---

## Project Architecture

### Technology Stack

- **Python:** 3.11+ (modern type hints, improved performance)
- **Package Manager:** `uv` (fast, modern alternative to pip)
- **CLI Framework:** `click` (command-line interface)
- **Terminal UI:** `rich` (beautiful output, tables, progress bars)
- **Data Processing:** `pandas` (CSV manipulation, data analysis)
- **HTTP:** `requests` (API calls)
- **Config:** `python-dotenv` (environment variables)
- **Testing:** `pytest` + `pytest-cov` (unit tests, coverage)
- **Linting:** `ruff` (fast Python linter)
- **Type Checking:** `mypy` (static type analysis)

### Project Structure

```
swim-data-tool/
├── pyproject.toml              # Project configuration (PEP 517/518)
├── VERSION                     # Semantic version (0.4.2)
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
│       │   └── usa_swimming.py # USA Swimming API client (IMPLEMENTED)
│       │
│       ├── commands/           # CLI command implementations
│       │   ├── __init__.py
│       │   ├── init.py         # Team initialization (IMPLEMENTED)
│       │   ├── status.py       # Status and config commands (IMPLEMENTED)
│       │   ├── roster.py       # Roster fetching (IMPLEMENTED)
│       │   ├── import_swimmer.py   # Single swimmer import (IMPLEMENTED)
│       │   ├── import_swimmers.py  # Batch import (IMPLEMENTED)
│       │   ├── classify.py     # Classify unattached (IMPLEMENTED)
│       │   └── generate.py     # Generate records (IMPLEMENTED)
│       │
│       ├── models/             # Data models
│       │   ├── __init__.py
│       │   └── events.py       # Event definitions and utilities (IMPLEMENTED)
│       │
│       ├── services/           # Business logic services
│       │   ├── __init__.py
│       │   └── record_generator.py  # Record generation service (IMPLEMENTED)
│       │
│       └── utils/              # Utility functions
│           └── __init__.py
│
├── templates/                  # Initialization templates (CREATED)
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
├── artifacts/                  # AI-generated documentation (development only)
│   ├── README.md               # Explains artifacts directory
│   ├── session-summary-v0.1-v0.3.md  # Testing guide
│   ├── v0.4.0-generate-records-plan.md
│   └── v0.4.0-release-summary.md
│
├── scratch/                    # Test and debug scripts (not committed)
│                               # Temporary scripts for development/testing
│                               # Move core functionality to proper modules when mature
│
├── docs/                       # Project documentation (future)
├── examples/                   # Usage examples (future)
└── .venv/                      # Virtual environment (not committed)
```

---

## Current State (v0.4.2)

### ✅ Fully Implemented Features

#### 1. Project Setup
- Modern `src/` layout structure
- `pyproject.toml` configuration (PEP 517/518 compliant)
- `uv` virtual environment
- Package installable with `uv pip install -e .`
- Git repository with remote on GitHub
- CI/CD with GitHub Actions

#### 2. Template System
- `env.template` - Environment variables with placeholders
- `.gitignore.template` - Standard ignore patterns
- `README.md.template` - Club repository documentation
- `claude.md.template` - AI assistant context for clubs
- `gitkeep.template` - Preserve empty directories

#### 3. init Command (`swim-data-tool init "Team Name"`)
- **Interactive team search via USA Swimming API**
  - Enter `?` for team code to search by swimmer name
  - Two-step API lookup: PersonKey → swim history → team codes
  - Formatted table display with team selection
  - Auto-fill team information after selection
- Creates complete directory structure
- Generates all configuration files from templates
- Version tracking with `.swim-data-tool-version`
- Displays formatted "Next Steps" with roster workflow

#### 4. roster Command (`swim-data-tool roster`) **NEW in v0.4.2**
- Fetches all swimmers who ever swam for the team
- Queries USA Swimming API across configured seasons
- `--seasons=all` option to query all years
- `--seasons=2024 --seasons=2025` for specific years
- Outputs to `data/lookups/roster.csv` by default
- Custom output path with `--output` option
- Shows formatted next steps panel with import instructions

#### 5. USA Swimming API Client (Production Ready)
- Real Sisense/Elasticube API integration
- Base URL: `https://bkzpf9l8qmjq.sg.qlikcloud.com`
- Authentication via hardcoded token
- `query_times_multi_year()` - efficient multi-year queries
- `download_swimmer_career()` - complete swimmer history with chunking
- `to_dataframe()` - convert API results to pandas DataFrames
- `search_swimmer_by_name()` - search for swimmers
- `get_swimmer_teams()` - extract team codes from swim history
- Optimized chunking strategy (1 call or 3 chunks based on result size)
- Automatic de-duplication
- `TeamInfo` dataclass model

#### 6. import swimmer Command (`swim-data-tool import swimmer <person-key>`)
- Downloads complete career data for one swimmer by PersonKey
- Saves to `data/raw/swimmers/name-personkey.csv`
- Uses years from .env (START_YEAR, END_YEAR)
- Rich progress output

#### 7. import swimmers Command (`swim-data-tool import swimmers`)
- **Smart defaults in v0.4.2:**
  - Defaults to `data/lookups/roster.csv` if no `--file` specified
  - No need to specify file when using roster workflow
- Reads CSV with columns: PersonKey, FullName
- Downloads career data for each swimmer
- **Performance monitoring:**
  - Real-time average download rate in progress bar
  - Slow swimmer detection (>30s warning)
  - Performance statistics in summary
- Progress tracking with resumability
- Skips already downloaded files
- `--dry-run` mode to preview
- Better interrupt handling (Ctrl+C)

#### 8. classify unattached Command (`swim-data-tool classify unattached`)
- Reads swimmer CSVs from `data/raw/swimmers/`
- Identifies first team-affiliated swim for each swimmer
- Classifies unattached swims:
  - **Probationary:** Before joining team, after another club
  - **Team-unattached:** After joining team
- Saves to `data/processed/unattached/probationary/` and `.../team-unattached/`
- Progress tracking with JSON log (resumable)
- Rich progress bars

#### 9. generate records Command (`swim-data-tool generate records`)
- Loads swimmer data from raw and processed directories
- Filters for team-affiliated swims (includes probationary)
- Parses and normalizes event data
- Groups by course (SCY, LCM, SCM), age group, and event
- Finds best time per swimmer per category
- Generates markdown files with formatted tables
- `--course=scy|lcm|scm` option to filter specific course
- Probationary swim indicators (‡)
- Saves to `data/records/{course}/records.md`

#### 10. Event Definitions Module (`models/events.py`)
- SCY, LCM, SCM event lists
- Age group mappings (10U, 11-12, 13-14, 15-16, 17-18, Open)
- Event parsing from API format ("50 FR SCY")
- Event code creation ("50-free")
- Time conversion utilities (MM:SS.SS to seconds)
- Age group determination

#### 11. Record Generation Service (`services/record_generator.py`)
- `RecordEntry` dataclass for record representation
- `RecordGenerator` class for processing
- Load swimmer data from multiple sources
- Filter team swims
- Parse and normalize events
- Calculate best times by event/age group
- Generate formatted markdown reports

#### 12. status & config Commands
- `swim-data-tool status` - Shows current configuration summary
- `swim-data-tool config` - Displays full .env file contents
- Both check for `.env` and guide user to init if missing

#### 13. Testing & Quality
- Test framework (pytest + pytest-cov)
- Tests for init command and templates (8 passing)
- Linting configuration (ruff)
- Type checking (mypy)
- GitHub Actions CI/CD
- All tests passing

---

## Complete Workflow Example

```bash
# Step 1: Initialize team repository
cd ~/swimming
mkdir my-team
cd my-team
swim-data-tool init "My Team Name"
# Enter '?' for team code to search interactively

# Step 2: Fetch team roster
swim-data-tool roster --seasons=all

# Step 3: Import all swimmers
swim-data-tool import swimmers
# Uses data/lookups/roster.csv by default

# Step 4: Classify unattached swims
swim-data-tool classify unattached

# Step 5: Generate records
swim-data-tool generate records

# Result: Records in data/records/{scy,lcm,scm}/records.md
```

---

## Version History

### v0.4.2 (Current) - 2025-10-07
- ✅ roster command for fetching team rosters
- ✅ Smart defaults for import swimmers (uses roster.csv)
- ✅ Performance monitoring during imports
- ✅ Consistent formatted output across all commands

### v0.4.1 - 2025-10-07
- ✅ Interactive team search in init command
- ✅ Two-step API integration for team discovery
- ✅ Smart team code suggestions

### v0.4.0 - 2025-10-07
- ✅ generate records command
- ✅ Event definitions module
- ✅ Record generation service
- ✅ Markdown output with formatted tables

### v0.3.0 - 2025-10-07
- ✅ classify unattached command
- ✅ Probationary vs team-unattached logic
- ✅ Progress tracking with JSON log

### v0.2.0 - 2025-10-07
- ✅ USA Swimming API client
- ✅ import swimmer command
- ✅ import swimmers command with batch processing

### v0.1.0 - 2025-10-07
- ✅ init command with templates
- ✅ Complete template system
- ✅ Directory structure creation

---

## Planned Features (v0.5.0+)

### Future Commands

1. **Top 10 Lists** (`generate top10`)
   - Top 10 all-time performers by event
   - Across all age groups
   - Individual files per event

2. **Annual Summaries** (`generate annual`)
   - Best times from specific season
   - New records set
   - Season highlights

3. **Publish Command** (`publish`)
   - Publish records to public GitHub repository
   - Git integration
   - Dry-run mode

---

## Multi-Club Architecture

### Design Philosophy

**swim-data-tool** is designed to work with multiple swim clubs from a single installation.

**Separation of Concerns:**
- **Tools repo** (`~/swimming/swim-data-tool`): Shared Python package, CLI tool
- **Club repos** (e.g., `~/swimming/ford`, `~/swimming/south-west-aquatic-sports`): Club-specific data only

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

# Or with uv (recommended)
cd ~/swimming/swim-data-tool
source .venv/bin/activate
cd ~/swimming/ford
swim-data-tool status
```

---

## Configuration (.env)

Each club has its own `.env` file (not committed to git):

```bash
# Club Information
CLUB_NAME="South West Aquatic Sports"
CLUB_ABBREVIATION="SWAS"
CLUB_NICKNAME="SWAS"

# USA Swimming
USA_SWIMMING_TEAM_CODE="AZ SWAS"
USA_SWIMMING_TEAM_NAMES="South West Aquatic Sports,SWAS"

# SwimCloud
SWIMCLOUD_TEAM_ID="10012795"

# LSC
LSC_CODE="AZ"
LSC_NAME="Arizona Swimming"

# Data Directories (relative to club repo root)
DATA_DIR="data"
RAW_DIR="data/raw"
PROCESSED_DIR="data/processed"
RECORDS_DIR="data/records"

# Collection Settings
START_YEAR="1998"
END_YEAR="2025"
COURSES="scy,lcm,scm"

# Tool Version (auto-managed)
SWIM_DATA_TOOL_VERSION="0.4.2"
```

---

## Development Workflow

### Setup

```bash
cd ~/swimming/swim-data-tool

# Activate virtual environment
source .venv/bin/activate

# Install in editable mode
uv pip install -e .

# Install dev dependencies
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
uv run pytest tests/test_commands/test_init.py
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

# Result: dist/swim_data_tool-0.4.2-py3-none-any.whl
```

### Releasing

```bash
# Update version
echo "0.4.3" > VERSION
# Update pyproject.toml version field
# Update CHANGELOG.md
# Update README.md
# Update this file (claude.md)

# Commit and tag
git add .
git commit -m "Release v0.4.3 - Description"
git tag v0.4.3
git push && git push --tags
```

---

## API Documentation

### USA Swimming API (Sisense/Elasticube)

**Base URL:** `https://bkzpf9l8qmjq.sg.qlikcloud.com/api/v1/data`

**Authentication:** Bearer token (hardcoded in `usa_swimming.py`)

**Key Methods:**
- `query_times_multi_year()` - Query swimmer times across multiple years
- `download_swimmer_career()` - Download complete career with chunking
- `search_swimmer_by_name()` - Search for swimmers by name
- `get_swimmer_teams()` - Extract team codes from swim history

**Rate Limiting:** Unknown (be conservative, add delays if needed)

---

## Data Flow

```
1. swim-data-tool init "Team Name"
   → Creates .env and directory structure

2. swim-data-tool roster --seasons=all
   → Fetches all swimmers
   → Saves to data/lookups/roster.csv

3. swim-data-tool import swimmers
   → Downloads from USA Swimming API
   → Saves to data/raw/swimmers/*.csv

4. swim-data-tool classify unattached
   → Reads data/raw/swimmers/*.csv
   → Classifies unattached swims
   → Saves to data/processed/unattached/

5. swim-data-tool generate records
   → Reads all data sources
   → Generates records
   → Saves to data/records/{course}/records.md
```

---

## Documentation & Artifact Guidelines

### AI Assistant Rules

**⚠️ IMPORTANT: Artifact management**

When working on swim-data-tool, AI assistants must follow these rules:

1. **Artifact Location**: All AI-generated task lists, design documents, and notes MUST go in `artifacts/`
2. **Root Directory Protection**: Do NOT create markdown files in the project root without explicit user approval
3. **Existing Files Only**: Only modify existing root-level files (README.md, CHANGELOG.md, claude.md) when necessary
4. **Naming Convention**: Use descriptive kebab-case names for artifacts

### Artifact Types

Store in `artifacts/`:
- Task lists and TODO tracking
- Design documents and planning
- Implementation notes
- Release summaries
- Session summaries for testing

### Protected Files

Only modify these root files when needed:
- `README.md` - User-facing documentation
- `CHANGELOG.md` - Version history (update on releases)
- `claude.md` - AI development context (update on major changes)
- `VERSION` - Version number (update on releases)

---

## Known Limitations & Future Work

### Current Limitations
- No World Aquatics integration yet (deferred)
- No relay events in records (future)
- No top 10 lists yet (v0.5.0)
- No annual summaries yet (v0.5.0)
- No publish command yet (v0.5.0)

### Planned Improvements
- Add relay event support
- Implement top 10 generation
- Add annual summary generation
- Create publish workflow
- Add more comprehensive tests
- Improve error handling and recovery
- Add API rate limiting protection

---

## Quick Reference

### Essential Commands

```bash
# Initialize new team
swim-data-tool init "Team Name"

# Fetch roster
swim-data-tool roster --seasons=all

# Import swimmers
swim-data-tool import swimmers

# Classify swims
swim-data-tool classify unattached

# Generate records
swim-data-tool generate records

# Check status
swim-data-tool status
swim-data-tool config
```

### File Locations

- Source code: `src/swim_data_tool/`
- Tests: `tests/`
- Templates: `templates/`
- Artifacts: `artifacts/` (AI-generated docs)
- Virtual environment: `.venv/`

### Important Files

- `pyproject.toml` - Project configuration
- `VERSION` - Current version number
- `CHANGELOG.md` - Version history
- `README.md` - User documentation
- `claude.md` - This file (AI context)

---

## Related Projects

### ford (private analysis repo)
**Location:** `/Users/aaryn/ford`  
**Status:** Original implementation, to be migrated

### south-west-aquatic-sports (private analysis repo)
**Location:** `~/swimming/south-west-aquatic-sports`  
**Status:** ✅ Initialized and being used for testing

### tucson-ford-dealers-aquatics-records (public repo)
**URL:** `https://github.com/aaryno/tucson-ford-dealers-aquatics-records.git`  
**Status:** Published records (no PII)

---

## Resources

### Documentation
- [uv Documentation](https://github.com/astral-sh/uv)
- [click Documentation](https://click.palletsprojects.com/)
- [rich Documentation](https://rich.readthedocs.io/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)

### Testing Guide
- See `artifacts/session-summary-v0.1-v0.3.md` for testing instructions
- See `artifacts/v0.4.0-release-summary.md` for generate records details

---

**Last Updated:** 2025-10-07  
**Version:** 0.4.2  
**Status:** Production-ready for core workflow