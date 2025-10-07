# Changelog

## [0.4.5] - 2025-10-07

### Added
- **Fully implemented enhanced `classify unattached` command**
  - Interactive mode with user prompts for 4 classification decisions
  - CLI flags for non-interactive mode (--high-school, --probationary, --college, --misc-unattached)
  - USA Swimming transfer rule logic:
    - Post-Jan 1, 2023: 60-day unattached period
    - Pre-Jan 1, 2023: 120-day unattached period
  - Four classification categories:
    - High School: Swims for high school teams
    - Probationary: Unattached swims within transfer window before joining club
    - College: Unattached swims during college years (ages 18-22)
    - Misc Unattached: All other unattached swims
  - Config file persistence (`.swim-data-tool-classify-config.json`)
    - Saves decisions for reuse
    - CLI flags override saved config
    - Version tracking
  - Classification metadata columns added to output CSVs:
    - `classification_category`: Category name
    - `classification_decision`: include or exclude
    - `classification_rationale`: Human-readable explanation
    - `transfer_rule_days`: 60 or 120 for probationary swims
  - Pre-analysis statistics showing swim breakdown by category
  - Enhanced summary output with decision tracking

### Changed
- **Output structure**: Changed from `data/processed/unattached/{probationary,team-unattached}/` to `data/processed/classified/{official,excluded}/`
- Classification now determines record eligibility based on user decisions
- All swims (club-affiliated and unattached) included in output with classification metadata

## [0.4.4] - 2025-10-07

### Documentation
- **Enhanced `classify unattached` command documentation**
  - Added interactive mode with user prompts for classification decisions
  - Added CLI flags for non-interactive mode (--high-school, --probationary, --college, --misc-unattached)
  - Documented USA Swimming transfer rules:
    - Post-Jan 1, 2023: 60-day unattached period
    - Pre-Jan 1, 2023: 120-day unattached period
  - Added 4 classification categories: High School, Probationary, College, Misc Unattached
  - Added `.swim-data-tool-classify-config.json` for saving classification decisions
  - Added classification metadata fields to Swim data model
  - New comprehensive "Classification Rules & Logic" section in claude.md
  - Updated data flow to use `data/processed/classified/{official,excluded}/`

## [0.4.3] - 2025-10-07

### Added
- **Consistent Next Steps panels across all commands**
  - Every command now shows what to do next in a green-bordered panel
  - Clear, actionable guidance throughout the workflow
  - Commands formatted in cyan for easy copy/paste
- **TODO for future relay recognition**
  - Added documentation for future feature to recognize individuals in relay results
  - Will enable crediting swimmers in team records and top 10 lists

### Improved
- **Enhanced output formatting for all commands**
  - classify: Added Next Steps panel with generate commands
  - generate: Added Next Steps with dynamic file paths and sharing instructions
  - All commands use consistent visual style (✓ checkmarks, clean layout)
- **Better import statistics and relay handling**
  - Import now skips relay entries (PersonKey=0) automatically
  - Clear breakdown: total entries, individual swimmers, relay-only entries
  - Shows "Already cached", "Will attempt", and "Previously attempted" counts
  - All numbers now add up correctly (no more confusion)

## [0.4.2] - 2025-10-07

### Added
- **Roster command** to fetch team rosters from USA Swimming
  - `swim-data-tool roster` fetches all swimmers who swam for the team
  - `--seasons=all` option to query all configured seasons
  - Outputs to `data/lookups/roster.csv` by default
  - Shows next steps in formatted panel
- **Import monitoring and performance tracking**
  - Real-time average download rate displayed in progress bar
  - Slow swimmer detection (>30s warning)
  - Performance statistics in summary output
  - Better interrupt handling (Ctrl+C)

### Changed
- `swim-data-tool import swimmers` now defaults to `data/lookups/roster.csv`
- No need to specify `--file` if using default roster location
- Updated "Next Steps" output formatting across all commands
  - Consistent green panels with clear instructions
  - init command shows roster workflow
  - roster command shows import options with example
  - import command shows classify and generate steps

### Improved
- Better user experience with consistent, nicely-formatted output
- Performance visibility during long-running imports
- Simplified command syntax with smart defaults

## [0.4.1] - 2025-10-07

### Added
- **Interactive team search via swimmer name lookup**
  - Two-step API integration: find PersonKey → query swims for team codes
  - Search trigger by entering `?` when prompted for team code
  - Display results in formatted table with team selection
  - Auto-fill team information after selection
- **Smart team code suggestion** based on club name patterns

### Fixed
- Fixed `search_swimmer_for_team()` to return actual team codes (not PersonKeys)
- Corrected API query structure for proper two-datasource lookup

## [0.4.0] - 2025-10-07

### Added
- **Implemented `generate records` command** for creating team records
  - Generates records by course (SCY, LCM, SCM)
  - Records organized by age group (10U, 11-12, 13-14, 15-16, 17-18, Open)
  - Markdown output with formatted tables
  - Course filtering with `--course` option
  - Probationary swim indicators (‡)
  - Saves to `data/records/{course}/records.md`
- **Event definitions module** (`models/events.py`)
  - SCY, LCM, SCM event lists
  - Age group mappings
  - Event parsing and formatting utilities
  - Time conversion functions
- **Record generation service** (`services/record_generator.py`)
  - Load swimmer data from raw and processed directories
  - Filter team-affiliated swims
  - Parse and normalize event data
  - Calculate best times per age group/event
  - Generate formatted markdown reports

### Changed
- Enhanced data processing pipeline to support record generation
- Added automatic course-based directory structure for records

## [0.3.0] - 2025-10-07

### Added
- **Implemented `classify unattached` command** for swim classification
  - Classifies unattached swims as probationary or team-unattached
  - Probationary: Unattached swims BEFORE joining team, AFTER another club
  - Team-unattached: Unattached swims AFTER joining team
  - Progress tracking with JSON log (resumable)
  - Rich progress bars during classification
  - Saves to `data/processed/unattached/probationary/` and `.../team-unattached/`

### Changed
- Enhanced classification logic based on proven ford implementation
- Automatic directory creation for processed data

## [0.2.0] - 2025-10-07

### Added
- **Implemented USA Swimming API client** with real Sisense/Elasticube integration
  - `query_times_multi_year()` for efficient multi-year queries
  - `download_swimmer_career()` for complete swimmer history
  - `to_dataframe()` for converting API results to pandas
  - Optimized chunking strategy (1 call or 3 chunks based on result size)
- **Implemented `import swimmer` command** for single swimmer downloads
  - Downloads complete career data by PersonKey
  - Saves to `data/raw/swimmers/` directory
  - Configurable year range from .env
- **Implemented `import swimmers` command** for batch downloads
  - Reads CSV file with PersonKeys and names
  - Progress bar with rich
  - Resumability (skips existing files)
  - Dry-run mode
  - Error handling and summary statistics

### Changed
- Enhanced USA Swimming API client with production-ready implementation
- Added pandas dependency for DataFrame handling

## [0.1.0] - 2025-10-07

### Added
- **Implemented `init` command** for initializing new team repositories
- Template system for generating team configuration files
  - `env.template` for environment configuration
  - `README.md.template` for team documentation
  - `claude.md.template` for AI assistant context
  - `.gitignore.template` for version control
  - `gitkeep.template` for preserving empty directories
- USA Swimming API client foundation (manual entry for now)
- Interactive prompts for team information collection
- Automatic directory structure creation
- Configuration file generation with variable substitution
- Tests for init command and templates
- Team info model with dataclass

### Changed
- Enhanced CLI with better rich output and panels
- Improved error handling and user feedback

## [0.0.1] - 2025-10-07

### Added
- Initial project structure
- CLI framework with click and rich
- Command structure for all planned features
- Basic `status` and `config` commands
- Development tooling (pytest, ruff, mypy)
