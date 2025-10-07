# Changelog

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
