# swim-data-tool

[![CI](https://github.com/aaryno/swim-data-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/aaryno/swim-data-tool/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](http://mypy-lang.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A modern Python CLI tool for swim team record management. Collect, process, and analyze swim data from USA Swimming and MaxPreps with a unified interface.

## Features

### 🏊 Multi-Source Data Collection
- **USA Swimming API** - Official swim times, team rosters, swimmer profiles
- **MaxPreps Integration** - High school swimming data with grade tracking
- Unified data model across all sources
- Automatic data normalization and deduplication

### 📊 Comprehensive Record Generation
- **Team Records** - All-time bests by age group and event
- **Top 10 Lists** - Best performers across all events
- **Annual Summaries** - Season-by-season analysis with records broken
- **Grade-Based Records** - High school format (Freshman, Sophomore, Junior, Senior)
- Support for all three courses: SCY, LCM, SCM

### 🎯 Smart Classification
- **Unattached Swims** - Interactive classification (high school, probationary, college)
- **Relay Support** - Automatic relay event detection and filtering
- **Name Consolidation** - Handles name variations and aliases

### 📤 Publishing & Sharing
- Export records to public GitHub repositories
- Custom README templates with placeholders
- Markdown-formatted outputs for easy sharing

### 🔧 Developer-Friendly
- Modern Python 3.11+ with full type hints
- Fast `uv` package manager
- Beautiful terminal UI with `rich`
- Comprehensive test suite with pytest
- CI/CD with GitHub Actions

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install swim-data-tool

```bash
# Clone the repository
git clone https://github.com/aaryno/swim-data-tool.git
cd swim-data-tool

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Quick Start

### 1. Initialize a New Team Repository

```bash
# Create a new team repository
mkdir my-swim-team
cd my-swim-team

# Initialize with interactive setup
swim-data-tool init "My Swim Team Name"
```

The init command will:
- Search for your team via USA Swimming API
- Create directory structure
- Generate configuration files (.env, README.md, claude.md)
- Set up data directories

### 2. Fetch Team Roster

```bash
# USA Swimming roster
swim-data-tool roster --source=usa_swimming

# MaxPreps roster (high school)
swim-data-tool roster --source=maxpreps --seasons=24-25

# Multiple seasons
swim-data-tool roster --source=maxpreps --start-season=20-21 --end-season=24-25
```

### 3. Import Swimmer Data

```bash
# Import all swimmers from roster
swim-data-tool import swimmers --source=usa_swimming

# Import specific swimmer by PersonKey
swim-data-tool import swimmer 123456

# Import from MaxPreps
swim-data-tool import swimmers --source=maxpreps
```

### 4. Classify Unattached Swims

```bash
# Interactive classification
swim-data-tool classify unattached

# Non-interactive with flags
swim-data-tool classify unattached \
  --high-school=exclude \
  --probationary=include \
  --college=exclude \
  --misc-unattached=exclude
```

### 5. Generate Records

```bash
# Generate all records
swim-data-tool generate records

# Specific course
swim-data-tool generate records --course=scy

# Top 10 lists
swim-data-tool generate top10
swim-data-tool generate top10 --n=25

# Annual summary for a season
swim-data-tool generate annual --season=2024
swim-data-tool generate annual --season=2024 --course=scy
```

### 6. Publish Records

```bash
# Publish to public repository
swim-data-tool publish

# Dry run (preview changes)
swim-data-tool publish --dry-run
```

## Command Reference

### Core Commands

| Command | Description |
|---------|-------------|
| `swim-data-tool init "Team Name"` | Initialize new team repository |
| `swim-data-tool status` | Show current status and configuration |
| `swim-data-tool config` | View .env configuration |

### Data Collection

| Command | Description |
|---------|-------------|
| `roster` | Fetch team roster from data source |
| `import swimmers` | Import career data for multiple swimmers |
| `import swimmer <PersonKey>` | Import single swimmer by PersonKey |

**Roster Options:**
- `--source=usa_swimming` or `--source=maxpreps` - Choose data source
- `--seasons=24-25 --seasons=23-24` - Specific seasons
- `--start-season=20-21 --end-season=24-25` - Season range
- `--output=FILE` - Custom output file

**Import Options:**
- `--source=usa_swimming` or `--source=maxpreps` - Choose data source
- `--file=FILE` - Custom roster file
- `--dry-run` - Preview without downloading
- `--force` - Re-download existing files

### Classification

| Command | Description |
|---------|-------------|
| `classify unattached` | Classify unattached swims for eligibility |

**Options:**
- `--high-school=include|exclude` - Include/exclude high school swims
- `--probationary=include|exclude` - Include/exclude probationary swims
- `--college=include|exclude` - Include/exclude college swims
- `--misc-unattached=include|exclude` - Include/exclude misc unattached

### Record Generation

| Command | Description |
|---------|-------------|
| `generate records` | Generate team records |
| `generate top10` | Generate top 10 all-time lists |
| `generate annual` | Generate annual season summary |

**Options:**
- `--course=scy|lcm|scm` - Specific course (default: all)
- `--n=NUMBER` - Number of swimmers in top N lists (default: 10)
- `--season=YEAR` - Season year for annual summary (required)

### Publishing

| Command | Description |
|---------|-------------|
| `publish` | Publish records to public repository |

**Options:**
- `--dry-run` - Preview changes without publishing

## Data Sources

### USA Swimming

**Supported:**
- Official swim times from USA Swimming database
- Team rosters with PersonKeys
- Swimmer career histories
- LSC and team information

**Requirements:**
- USA Swimming API token (Sisense JWT)
- Team code (e.g., "SWAS")
- LSC code (e.g., "AZ")

**Configuration (.env):**
```bash
USA_SWIMMING_TOKEN=your_jwt_token_here
USA_SWIMMING_TEAM_CODE=YOUR_TEAM_CODE
LSC_CODE=XX
START_YEAR=2000
END_YEAR=2025
```

### MaxPreps

**Supported:**
- High school swim team rosters with grades
- Individual athlete statistics
- Season-by-season data
- Boys and girls teams

**Requirements:**
- MaxPreps school slug (from URL)
- City and state information
- Playwright for web scraping

**Configuration (.env):**
```bash
MAXPREPS_SCHOOL_SLUG=your-school-name
MAXPREPS_CITY=phoenix
MAXPREPS_STATE=arizona
MAXPREPS_GENDER=boys  # or "girls" or "both"
```

## Project Structure

When you initialize a team repository with `swim-data-tool init`, the following structure is created:

```
my-swim-team/
├── .env                        # Configuration (NOT committed)
├── .gitignore                  # Git ignore patterns
├── README.md                   # Team documentation
├── claude.md                   # AI assistant context
├── data/
│   ├── raw/                    # Raw API data (NOT committed)
│   │   └── swimmers/           # Individual swimmer CSVs
│   ├── processed/              # Processed data (NOT committed)
│   │   └── unattached/         # Classified unattached swims
│   ├── records/                # Generated records (committed)
│   │   ├── scy/                # Short course yards
│   │   ├── lcm/                # Long course meters
│   │   └── scm/                # Short course meters
│   ├── reports/                # Analysis reports (committed)
│   └── lookups/                # Reference data (committed)
│       └── roster.csv          # Team roster
└── logs/                       # Processing logs (NOT committed)
```

## Configuration

All team-specific configuration is stored in `.env` files:

```bash
# Required for USA Swimming
USA_SWIMMING_TOKEN=your_sisense_jwt_token
USA_SWIMMING_TEAM_CODE=YOUR_TEAM
LSC_CODE=XX
START_YEAR=2000
END_YEAR=2025

# Optional for MaxPreps
MAXPREPS_SCHOOL_SLUG=your-school
MAXPREPS_CITY=city
MAXPREPS_STATE=state
MAXPREPS_GENDER=boys

# Optional for publishing
PUBLIC_REPO_URL=https://github.com/yourusername/team-records
PUBLIC_REPO_PATH=/path/to/local/clone

# Team metadata
CLUB_NAME=My Swim Team
CLUB_ABBREVIATION=MST
SWIMCLOUD_TEAM_ID=12345678
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/aaryno/swim-data-tool.git
cd swim-data-tool

# Create virtual environment
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=swim_data_tool --cov-report=term-missing

# Run specific test file
pytest tests/test_commands/test_init.py
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
ruff format .

# Type check with mypy
mypy src/swim_data_tool
```

### CI/CD

The project uses GitHub Actions for continuous integration:
- **Lint**: Ruff linting and formatting checks
- **Type Check**: Mypy static type analysis
- **Test**: Pytest on Python 3.11 and 3.12

## Privacy & Security

**⚠️ Important:** Team repositories contain personally identifiable information (PII):
- Swimmer names
- Dates of birth (in some cases)
- USA Swimming PersonKeys

**Best Practices:**
- Keep team repositories **private**
- Never commit `.env` files
- Never commit `data/raw/` directory
- Only publish aggregate records (no individual PII)
- Use `.gitignore` to exclude sensitive data

## API Token Management

### USA Swimming Token

The USA Swimming API requires a Sisense JWT token. See [docs/UPDATE_API_TOKEN.md](docs/UPDATE_API_TOKEN.md) for:
- How to obtain a token
- Token validation
- Troubleshooting expired tokens

## Use Cases

### Club Teams (USA Swimming)
- Track team records across age groups
- Generate top 10 all-time performer lists
- Classify unattached swims for eligibility
- Publish records to public websites

### High School Teams (MaxPreps)
- Collect data from MaxPreps team pages
- Generate grade-based records
- Track season-by-season progression
- Create annual summaries with records broken

### Multi-Team Organizations
- Manage multiple team repositories
- Compare performance across teams
- Aggregate data for LSC or district analysis

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass and linting is clean
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version:** 0.12.1

**Recent Highlights:**
- v0.12.1: CI/CD pipeline fixes, full ruff and mypy compliance
- v0.12.0: Relay filtering fix, custom README templates
- v0.11.0: High school swimming support with grade tracking
- v0.10.0: Multi-source architecture with MaxPreps integration
- v0.9.0: Critical roster deduplication and .env loading fixes

## Support

For issues, questions, or feature requests, please [open an issue](https://github.com/aaryno/swim-data-tool/issues) on GitHub.

---

**Built with:** Python 3.11+ • Click • Rich • Pandas • uv • Ruff • Mypy • Pytest
