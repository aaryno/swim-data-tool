# Changelog

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
