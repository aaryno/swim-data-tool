# swim-data-tool Development Session Summary

**Date:** 2025-10-07  
**Versions Completed:** v0.1.0, v0.2.0, v0.3.0  
**Status:** Ready for testing with real team data

---

## What Was Built

### v0.1.0 - Init Command ✅

**Purpose:** Initialize new team repositories with proper structure

**Command:**
```bash
swim-data-tool init "Team Name"
```

**What it does:**
- Interactive prompts for team information (name, LSC, team code, SwimCloud ID)
- Creates directory structure:
  - `data/raw/swimmers/` - For downloaded swimmer CSVs
  - `data/processed/unattached/` - For classified swims
  - `data/records/` - For generated records
  - `logs/` - For log files
- Generates configuration files:
  - `.env` - Team configuration (not committed)
  - `README.md` - Team documentation
  - `claude.md` - AI assistant context
  - `.gitignore` - Git ignore patterns
  - `.swim-data-tool-version` - Tool version tracking

**Templates created:**
- `env.template` - Environment configuration
- `README.md.template` - Team README
- `claude.md.template` - AI context for teams
- `.gitignore.template` - Git ignore
- `gitkeep.template` - Directory preservation

---

### v0.2.0 - Import Commands ✅

**Purpose:** Download swimmer data from USA Swimming API

#### Command 1: Import Single Swimmer
```bash
swim-data-tool import swimmer <person-key>
```

**What it does:**
- Downloads complete career data for one swimmer by PersonKey
- Saves to `data/raw/swimmers/name-personkey.csv`
- Uses years from .env (START_YEAR, END_YEAR)

#### Command 2: Import Multiple Swimmers
```bash
swim-data-tool import swimmers --file=swimmers.csv [--dry-run]
```

**What it does:**
- Reads CSV with columns: PersonKey, FullName
- Downloads career data for each swimmer
- Progress bar with rich
- Resumability (skips already downloaded)
- Dry-run mode to preview

**USA Swimming API Client:**
- Real Sisense/Elasticube API integration
- `query_times_multi_year()` - Multi-year queries in one call
- `download_swimmer_career()` - Complete career download
- Optimized chunking (1 call or 3 chunks based on data size)
- Automatic de-duplication

**CSV Input Format:**
```csv
PersonKey,FullName
123456,John Doe
234567,Jane Smith
```

---

### v0.3.0 - Classify Command ✅

**Purpose:** Classify unattached swims as probationary or team-unattached

**Command:**
```bash
swim-data-tool classify unattached
```

**What it does:**
- Reads all swimmer CSVs from `data/raw/swimmers/`
- Finds first team swim for each swimmer
- Classifies unattached swims:
  - **Probationary**: Unattached BEFORE joining team, AFTER another club
  - **Team-unattached**: Unattached AFTER joining team
- Saves to:
  - `data/processed/unattached/probationary/`
  - `data/processed/unattached/{team}-unattached/`
- Progress tracking with JSON log (resumable)
- Rich progress bars

**Classification Logic:**
```
1. Find first swim where Team matches configured team names
2. Before first team swim:
   - If swimmer was at another club before → unattached = Probationary
3. After first team swim:
   - All unattached swims = Team-unattached
```

---

## How to Test with a New Team

### Step 1: Install swim-data-tool

```bash
cd ~/swimming/swim-data-tool
source .venv/bin/activate
uv pip install -e .
```

### Step 2: Create New Team Directory

```bash
cd ~/swimming
mkdir new-team-name
cd new-team-name
```

### Step 3: Initialize Team Repository

```bash
swim-data-tool init "Full Team Name"
```

Follow the interactive prompts to enter:
- Full club name
- Club abbreviation (e.g., "TFDA")
- Club nickname
- USA Swimming team code (e.g., "AZ FORD")
- LSC code (e.g., "AZ")
- LSC name (e.g., "Arizona Swimming")
- SwimCloud team ID (optional)
- Data collection years (e.g., 1998-2025)

### Step 4: Verify Configuration

```bash
swim-data-tool status
swim-data-tool config
```

### Step 5: Create Swimmer List CSV

Create `swimmers.csv` with PersonKeys and names:

```csv
PersonKey,FullName
123456,John Doe
234567,Jane Smith
345678,Bob Johnson
```

**How to find PersonKeys:**
- Go to times.usaswimming.org
- Search for team and year
- Click on swimmer name
- PersonKey is in the URL: `.../personKey=123456`

### Step 6: Import Swimmer Data (Dry Run First)

```bash
# Preview what will be downloaded
swim-data-tool import swimmers --file=swimmers.csv --dry-run

# Actually download
swim-data-tool import swimmers --file=swimmers.csv
```

**Expected output:**
- Progress bar showing download status
- CSVs saved to `data/raw/swimmers/`
- Summary statistics

### Step 7: Classify Unattached Swims

```bash
swim-data-tool classify unattached
```

**Expected output:**
- Progress bar showing classification
- CSVs saved to `data/processed/unattached/probationary/`
- CSVs saved to `data/processed/unattached/{team}-unattached/`
- Summary statistics

---

## Configuration (.env)

Key environment variables:

```bash
# Club Information
CLUB_NAME="Full Team Name"
CLUB_ABBREVIATION="ABBR"
USA_SWIMMING_TEAM_CODE="STATE CODE"
USA_SWIMMING_TEAM_NAMES="Full Name,Abbr,Nickname"  # Comma-separated

# Data Collection
START_YEAR="1998"
END_YEAR="2025"

# Directories (relative paths)
RAW_DIR="data/raw"
PROCESSED_DIR="data/processed"
RECORDS_DIR="data/records"
```

---

## Common Issues & Solutions

### Issue: No swimmers found
**Solution:** Check that swimmers.csv has correct format with PersonKey column

### Issue: Import fails with 404 error
**Solution:** Verify PersonKey is correct (try manually in times.usaswimming.org)

### Issue: Classification finds no unattached swims
**Solution:** This is normal if swimmers only have team-affiliated swims

### Issue: Tool not found after install
**Solution:** Make sure virtual environment is activated: `source .venv/bin/activate`

---

## Data Flow Summary

```
1. swim-data-tool init
   → Creates directory structure and .env

2. Create swimmers.csv with PersonKeys

3. swim-data-tool import swimmers --file=swimmers.csv
   → Downloads from USA Swimming API
   → Saves to data/raw/swimmers/*.csv

4. swim-data-tool classify unattached
   → Reads data/raw/swimmers/*.csv
   → Classifies unattached swims
   → Saves to data/processed/unattached/
```

---

## File Structure After Running All Commands

```
new-team-name/
├── .env                           # Configuration (not committed)
├── .gitignore                     # Git ignore
├── README.md                      # Team documentation
├── claude.md                      # AI context
├── .swim-data-tool-version        # Tool version
│
├── data/
│   ├── raw/
│   │   └── swimmers/              # Downloaded swimmer CSVs
│   │       ├── john-doe-123456.csv
│   │       └── jane-smith-234567.csv
│   │
│   ├── processed/
│   │   └── unattached/
│   │       ├── probationary/      # Probationary swims
│   │       └── team-unattached/   # Team-unattached swims
│   │
│   └── records/                   # (Empty - for v0.4.0)
│
└── logs/                          # Progress logs
```

---

## What's NOT Yet Implemented

**v0.4.0 - Generate Records (In Progress)**
- Generate team records by course/age group/event
- Top 10 all-time lists
- Annual summaries

**v0.5.0 - Publish (Future)**
- Publish records to public repository
- Git integration

---

## Quick Reference Commands

```bash
# Check version
swim-data-tool --version

# Show status
swim-data-tool status

# View config
swim-data-tool config

# Import single swimmer
swim-data-tool import swimmer <person-key>

# Import multiple swimmers
swim-data-tool import swimmers --file=swimmers.csv

# Classify unattached swims
swim-data-tool classify unattached

# Help
swim-data-tool --help
swim-data-tool import --help
swim-data-tool classify --help
```

---

## Success Criteria for Testing

✅ **Init successful if:**
- Directory structure created
- .env file generated with correct values
- README.md and claude.md present

✅ **Import successful if:**
- CSV files created in data/raw/swimmers/
- Files named: `swimmer-name-personkey.csv`
- CSVs contain swim data with columns: Name, Event, SwimTime, Team, etc.

✅ **Classify successful if:**
- CSV files created in data/processed/unattached/
- Probationary directory has swims before team join date
- Team-unattached directory has swims after team join date
- classification_progress.json created with summary

---

## Testing Notes

**Recommended test approach:**
1. Start with 3-5 swimmers (quick test)
2. Include swimmers with varied histories:
   - Swimmer who started on team (no probationary)
   - Swimmer who came from another club (has probationary)
   - Swimmer with unattached swims after joining team
3. Verify CSV outputs are correct
4. Test resumability by interrupting and restarting

**Expected timing:**
- Init: < 1 second
- Import: ~2-3 seconds per swimmer
- Classify: ~0.1 second per swimmer

---

## Support & References

- **Main docs:** `~/swimming/swim-data-tool/README.md`
- **AI context:** `~/swimming/swim-data-tool/claude.md`
- **Changelog:** `~/swimming/swim-data-tool/CHANGELOG.md`
- **GitHub:** https://github.com/aaryno/swim-data-tool (private)

---

**Status:** Ready for real-world testing!  
**Next Step:** Test with actual team data to validate v0.1.0-v0.3.0 functionality
