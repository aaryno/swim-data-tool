# Changelog

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
