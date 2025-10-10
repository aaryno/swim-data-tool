# Changelog

## [0.12.2] - 2025-10-09

### Fixed
- Added missing `services/__init__.py` to make services directory a proper Python package
- Modernized version management using `importlib.metadata` with fallback to VERSION file

### Changed
- Updated README.md with comprehensive tool documentation and GitHub badges
- Updated claude.md with current version (0.12.1 → 0.12.2) and recent version history

## [0.12.1] - 2025-10-09

### Fixed
- CI/CD pipeline now passing all checks (lint, type-check, tests)
- Auto-fixed 225+ ruff linting errors (trailing whitespace, f-strings, line length, import sorting)
- Added `pandas-stubs` to dev dependencies for mypy type checking

### Changed
- Cleaned up repository by removing test scripts and outdated documentation files
- Improved code quality and consistency across codebase

## [0.12.0] - 2025-10-09

### Fixed
- **Critical: Relay events contaminating individual top 10 lists** - Fixed relay events (200 FR RELAY, 400 FR RELAY, 200 MEDLEY RELAY) appearing in individual event top 10 lists
  - Added explicit relay filtering in `generate_top10.py` and `generate_all_season_top10.py`
  - Filters out events containing "RELAY" from individual top 10 lists
  - Relay events remain in their own dedicated relay records and in annual summaries
  - Affected all teams using top 10 generation
  - Impact: 1,870+ relay swims correctly filtered in typical high school dataset

### Added
- **Custom README template support** - Publish command now supports custom README templates
  - Checks for `README-template.md` in team directory
  - Uses custom template with `{DATE}` placeholder if found
  - Falls back to auto-generated README if no template exists
  - Enables teams (especially high schools) to create comprehensive custom documentation
  - Template survives future publish operations

## [0.11.0] - 2025-10-09

### Added
- **High School Swimming Support** - Complete pipeline for MaxPreps and AIA data
  - Dynamic grade assignment based on season sections
  - Relay data capture from individual athlete pages
  - AIA State Championship PDF parsing and integration
  - Comprehensive name consolidation with alias management

### Changed
- Grade-based records generation for high school format
- Enhanced annual summaries with records broken section
- Improved time and date formatting across all outputs

## [0.10.0] - 2025-10-08

### Added
- **Season Range Support** - New `--start-season` and `--end-season` flags for roster command
  - Simplifies multi-season collection (e.g., `--start-season=12-13 --end-season=24-25` expands to 13 seasons)
  - Works with MaxPreps YY-YY format and USA Swimming YYYY format
  - Validation ensures both parameters provided together
  - More convenient than multiple `--seasons` flags
- **Multi-Source Architecture** - Abstract data source layer for USA Swimming and MaxPreps
  - `SwimDataSource` abstract base class in `sources/base.py`
  - Canonical data models in `models/canonical.py` (Swimmer, Swim, Team)
  - Source factory pattern in `sources/factory.py`
  - `USASwimmingSource` plugin (refactored from direct API calls)
  - `MaxPrepsSource` plugin (web scraping with Playwright)
- **MaxPreps Integration** - Full support for high school swimming data
  - Roster scraping from MaxPreps team pages
  - Athlete stats scraping from individual athlete pages
  - Grade level tracking (Freshman, Sophomore, Junior, Senior)
  - Season deduplication (keeps most recent grade)
  - Both boys and girls teams supported
- **Grade-Based Data** - Support for grade levels in data models
  - Grade information extracted from MaxPreps rosters
  - Numeric grades (9, 10, 11, 12) and abbreviations (Fr., So., Jr., Sr.)
  - Foundation for grade-based record generation

### Changed
- Roster command now supports `--source` flag (defaults to `usa_swimming`)
- Import swimmers command updated to support multiple data sources
- CLI examples updated to show MaxPreps usage
- Testing documentation expanded with season range tests

### Documentation
- `SEASON_RANGE_FEATURE.md` - Season range implementation guide
- `TESTING.md` - Updated with season range test cases
- `tanque-verde-test/SEASON_RANGE_TESTS.md` - Quick testing guide
- `research/MAXPREPS_API_ANALYSIS.md` - MaxPreps data structure research
- `research/CLI_WORKFLOW.md` - Multi-source command-line patterns

## [0.9.0] - 2025-10-08

### Fixed
- **Critical: Roster command not loading .env file** - Fixed roster command to properly call `load_dotenv()` after checking for .env file existence
  - Bug caused START_YEAR and END_YEAR to not be loaded from .env
  - Resulted in incorrect year ranges (e.g., "20000-2025" instead of "2000-2025")
  - `--seasons=all` flag was affected
- **Critical: Roster deduplication removing swimmers** - Fixed deduplication logic to group by PersonKey only (not PersonKey + FullName)
  - Previous bug caused swimmers with name variations to be treated as duplicates and removed
  - Multi-year rosters would paradoxically return fewer swimmers than single-year rosters
  - Example: 514 swimmers (2025) → 288 swimmers (2024-2025) before fix

### Added
- Documentation for API token management in `docs/UPDATE_API_TOKEN.md`
- Token validation script in `scratch/validate_current_token.py`
- Comprehensive session artifact documenting bug discovery and fixes

### Changed
- Updated AUTH_TOKEN with fresh token (2025-10-08)
- Improved roster command robustness

## [0.8.1] - 2025-10-08

### Improved
- **Enhanced publish README generation** with detailed links to top10 and annual summaries
  - Top10 lists now organized by course → gender → individual events
  - Annual summaries organized by year → course → gender
  - Direct links to each top10 event file (not just directories)
  - Better formatting and navigation in published records
  - Event names automatically formatted (e.g., "50-free" → "50 Free")

### Changed
- Publish command now generates comprehensive README with full navigation structure
- Users can now easily browse all top10 events and season summaries from the README

## [0.8.0] - 2025-10-08

### Added
- **Verified top10 lists generation** - Fully operational and tested with SWAS team (92 files)
- **Complete v0.7.0 annual summary implementation** - All three parts working correctly

### Status
- ✅ All core features production-ready
- ✅ Gender-separated records, top10, and annual summaries
- ✅ Comprehensive testing completed

## [0.7.0] - 2025-10-08

### Added
- **Comprehensive annual summary format** matching professional records reports
  - Part 1: All records broken in chronological order with detailed information
  - Part 2: Standing records tables grouped by age group
  - Summary statistics with record breaker counts and breakdowns by type
  - Improved season header with "YYYY-YYYY Season Records Summary" format
  - Legend with probationary, unattached, and international swim indicators

### Changed
- `generate annual` command now produces comprehensive summaries with:
  - Chronologically ordered list of all records broken during season
  - Standing records table showing current team records from that season
  - Detailed statistics: total broken, still standing, top record breakers
  - Enhanced formatting matching official swim team record publications
- Annual summaries now include proper season date ranges (Sept 1 - Aug 31)

### Improved
- Better record identification logic (includes ties as records)
- More detailed meet information display
- Professional formatting for season summaries
- Consistent legend across all annual summary files

## [0.6.3] - 2025-10-07

### Changed
- **Enhanced UNOFFICIAL disclaimers in published README.md**
  - Prominent warning at top: "⚠️ UNOFFICIAL RECORDS - INTERNAL REVIEW ONLY"
  - Requires verification by club administrators before official use
  - NO WARRANTY disclaimer added
  - Internal use only notice
  - Not approved for external distribution or official team communications

### Important
- All published records now clearly marked as UNOFFICIAL
- Strong disclaimers ensure proper expectations for internal review
- Club administrators must verify before any official use

## [0.6.2] - 2025-10-07

### Added
- `--force` flag for `import swimmers` command to re-download all swimmers and overwrite existing files
- Helper script in scratch directory to add Gender column to existing swimmer CSVs without re-downloading
- **Auto-generated README.md in publish command**: Professional README with organized links to all records
- Publish instructions in `generate records` Next Steps output

### Changed
- `publish` command now automatically creates/updates README.md with:
  - **⚠️ UNOFFICIAL RECORDS - INTERNAL REVIEW ONLY** warning at top
  - **Verification requirements** by club administrators
  - **NO WARRANTY disclaimer** and internal use only notice
  - Team name and last updated date
  - Links to all records (boys, girls, combined) by course
  - Links to top 10 lists and annual summaries
  - Privacy notice and repository structure documentation
- `generate records` Next Steps now includes publish workflow with .env configuration examples
- Updated documentation to reflect that gender must be added to existing swimmer CSVs before regenerating records

### Important
- **Published records are UNOFFICIAL and require club administrator verification**
- README emphasizes these are for internal review only
- Not approved for external distribution or official team use

### Improved
- Next Steps panels now use `expand=False` to prevent wrapping on narrow terminals
- All test/debug scripts moved to `scratch/` directory for better organization

### Notes
- For existing teams: Add Gender to swimmer CSVs, re-run `classify unattached`, then `generate records`
- New teams will automatically get Gender column from roster on first import

## [0.6.1] - 2025-10-07

### Fixed
- **Gender extraction now working correctly**: Extract gender from `EventCompetitionCategoryKey` field in swim data
  - USA Swimming separates events by gender: 1 = Female, 2 = Male
  - Gender is now automatically populated in roster and swimmer CSVs
  - No separate API call needed - gender comes from event data itself
- Removed unused `get_gender_for_persons()` method that didn't work
- API returns EventCompetitionCategoryKey as strings, not integers - mapping now handles both

### Technical Details
- Gender is extracted directly from USA Swimming's event categorization system
- All events are pre-separated by gender, so every swim record contains gender information
- This is more reliable than attempting to query a separate gender field

## [0.6.0] - 2025-10-07

### Added
- **Gender Support**: All commands now fetch and use gender information
- `USASwimmingAPI.get_gender_for_persons()`: Batch fetch gender from Public Person Search datasource
- Gender column in roster CSV output
- Gender statistics in roster command output

### Changed
- **BREAKING: Record generation now splits by gender**
  - `generate records` creates separate `records-boys.md` and `records-girls.md` files
  - `generate top10` creates separate `top10/{course}/boys/` and `top10/{course}/girls/` directories
  - `generate annual` creates separate `{year}-{course}-boys.md` and `{year}-{course}-girls.md` files
  - Legacy combined records (no gender) still supported if Gender column missing
- `roster` command now fetches gender for all swimmers
- `import swimmers` preserves Gender column in downloaded CSVs
- Gender statistics displayed during record generation

### Improved
- Records now properly separate boys/girls times as per USA Swimming standards
- Clear gender labeling in all generated markdown files
- Backwards compatible with existing data (falls back to combined records if no gender data)

## [0.5.0] - 2025-10-07

### Added
- **Top 10 All-Time Lists** (`generate top10`)
  - Generates top N performers for each event across all age groups
  - Separate markdown files per event: `data/records/top10/{course}/{event}.md`
  - Customizable with `--n` option (default: 10)
  - Ranks swimmers with best time per swimmer (no duplicates)
  - Includes probationary swim indicators (‡)
  - Rich progress output and formatted next steps panel
- **Annual Season Summaries** (`generate annual`)
  - Generates season-specific summaries with best times
  - Compares against all-time team records to identify new records
  - Highlights new records set during the season
  - Best times by age group for the season
  - Requires `--season` parameter (e.g., `--season=2024`)
  - Optional `--course` filter for specific course
  - Saves to `data/records/annual/{year}-{course}.md`
  - Rich formatted output with tables and panels
- **Publish Command** (`publish`)
  - Publishes records to public GitHub repository
  - Clones or pulls latest from configured PUBLIC_REPO_URL
  - Copies all markdown files from `data/records/` to public repo
  - Commits with timestamp and pushes to GitHub
  - `--dry-run` mode to preview without making changes
  - Requires git installation and SSH keys configured
  - Configuration via PUBLIC_REPO_URL and PUBLIC_REPO_LOCAL in .env
  - Formatted next steps with repo link
- **Extended RecordGenerator Service**
  - `get_top_n_by_event()` - Get top N performers across all ages
  - `generate_top10_markdown()` - Generate top N list markdown
  - `filter_by_season()` - Filter swims by year
  - `generate_annual_summary_markdown()` - Generate season summary markdown
  - Record comparison logic for identifying new records

### Changed
- Enhanced generate commands with consistent UX patterns
- All generate commands now show formatted next steps panels
- Improved markdown formatting for readability

### Documentation
- Added v0.5.0 implementation plan in artifacts/
- Updated README with new commands
- Updated claude.md with v0.5.0 features

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
