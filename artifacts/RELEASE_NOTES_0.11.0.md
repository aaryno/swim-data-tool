# Release 0.11.0 - High School Swimming Support

**Release Date:** October 9, 2025

## 🎉 Major Features

### MaxPreps Data Source
- **NEW:** Complete MaxPreps web scraper for high school swimming data
- Fetches current season results and historical data from athlete profile pages
- Automatically detects and assigns season-specific grades (Freshman, Sophomore, Junior, Senior)
- Handles both boys and girls swimming with different URL paths
- Event normalization to standard format (100 Breast → 100 BR SCY)

### AIA State Championship Integration
- **NEW:** PDF parser for Arizona Interscholastic Association (AIA) state meet results
- Extracts data from 24 years of state championship PDFs (2001-2024)
- Includes swimmer names, grades, times, splits, and place finishes
- Automatic school-specific filtering
- Complements MaxPreps data with official state meet results

### Swimmer Name Consolidation
- **NEW:** Intelligent duplicate detection based on nickname patterns
- Interactive consolidation tool with user confirmation
- Persistent alias mapping (swimmer_aliases.json)
- Supports 15+ common nickname variations (Nick/Nicholas, Sam/Samuel, etc.)
- Automatic alias application on future imports

### High School Record Generation
- **NEW:** Grade-based record categories (Freshman, Sophomore, Junior, Senior, Open)
- Bold formatting for Open (all-time) records
- 8 standard high school events supported
- Clean time formatting (56.59 not 00:56.59)
- Separate boys and girls records

### Top 10 Lists
- **NEW:** All-time top 10 lists with complete historical coverage
- **NEW:** Current season top 10 lists
- Best time per swimmer (no duplicates)
- Year labels (FR/SO/JR/SR) instead of grade numbers
- Ranked 1-10 by time

### Annual Season Summaries
- **NEW:** Comprehensive season overview with statistics
- Records broken detection and display
- Side-by-side boys/girls best times table
- Meet schedule with dates
- Active roster by grade
- Participation statistics

## 🔧 Enhancements

### Time & Date Formatting
- Consistent two-decimal precision on all times (52.68)
- Remove leading zeros (56.59 not 00:56.59, 1:00.60 not 01:00.60)
- Omit minutes for times under 1:00
- Right-justified times in tables
- Date display without time component (Oct 23, 2021)
- Shared `time_formatter.py` module for consistency

### Data Quality
- Season-specific grade assignment from MaxPreps sections
- Grade inference for graduated swimmers (work backward from senior year)
- Duplicate swim removal (same event, date, time)
- Cross-source data merging (MaxPreps + AIA)

### Publishing
- Simplified directory structure (all records at top level)
- Formatted README with tables linking to all records
- GitHub integration with automatic publishing

## 📝 Data Sources

### MaxPreps (maxpreps.com)
- Current season results
- Athlete career pages
- Season-by-season breakdown
- Meet names and dates

### AIA State Championships
- 24 years of PDF results (2001-2024)
- Official state meet times
- Grade verification
- Historical coverage

## 🛠️ Tools Created

### Parser Scripts
- `parse_aia_state_meets.py` - Extract from AIA PDFs
- `merge_aia_state_data.py` - Merge AIA data into swimmers

### Name Management
- `detect_name_duplicates.py` - Find swimmer variations
- `consolidate_swimmers.py` - Interactive merge tool

### Record Generation
- `generate_hs_records.py` - Grade-based team records
- `generate_top10.py` - Top 10 lists (all-time + season)
- `generate_annual_summary.py` - Season summary reports

### Utilities
- `time_formatter.py` - Shared formatting functions

## 📊 Statistics

Example deployment (Tanque Verde High School):
- 2,129 total swims processed
- 24 years of historical data (2001-2025)
- 10 duplicate swimmers consolidated
- 61 AIA state meet swims extracted
- 70+ active swimmers tracked

## 🔄 Workflow

```bash
# After each meet:
swim-data-tool import swimmers --file=data/lookups/roster-maxpreps.csv
python3 generate_hs_records.py
python3 generate_top10.py
python3 generate_annual_summary.py
swim-data-tool publish

# At end of season:
python3 parse_aia_state_meets.py
python3 merge_aia_state_data.py
python3 detect_name_duplicates.py
python3 consolidate_swimmers.py  # if duplicates found
# Then regenerate and publish
```

## 🎯 Use Cases

This release is specifically designed for:
- High school swim teams
- High school coaches and administrators
- Teams using MaxPreps for meet results
- Arizona high school teams (with AIA state meet integration)
- Teams needing grade-based records
- Teams wanting historical record tracking

## 📦 Breaking Changes

None. This is a feature addition release. Existing USA Swimming source remains fully functional.

## 🐛 Bug Fixes

- Fixed grade assignment for historical swims
- Corrected MaxPreps URL path detection (boys vs girls)
- Improved event name normalization
- Fixed duplicate detection for exact same swims

## 📚 Documentation

New documentation files:
- `MAXPREPS_WORKFLOW.md` - MaxPreps integration guide
- `MAXPREPS_RECORDS_PLAN.md` - Record generation planning
- `SWIMMER_CONSOLIDATION.md` - Name consolidation summary
- `RECORDS_STRUCTURE.md` - Published records organization
- `research/aia-swimming.md` - AIA data source research

## 🙏 Acknowledgments

Developed for Tanque Verde High School Swimming (Tucson, Arizona) as the initial deployment and test case.

---

**Full Changelog:** https://github.com/aaryno/swim-data-tool/compare/v0.10.0...v0.11.0

