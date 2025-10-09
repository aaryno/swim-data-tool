# Testing Guide - Multi-Source Implementation

**Date:** October 8, 2025  
**Status:** Ready for testing!

---

## 🧪 What You Can Test Now

### ✅ Currently Testable

1. **USA Swimming Roster** (backwards compatibility)
2. **MaxPreps Roster** (new functionality)  
3. **Source Factory** (Python module testing)
4. **Canonical Data Models** (Python module testing)

### ⏳ Previously Not Testable (Now Available! ✅)

- ~~Import swimmers~~ **NOW TESTABLE!** ✅
- ~~End-to-end record generation~~ **NOW TESTABLE!** ✅

### 🆕 New Features (October 8, 2025)

- **Season Range Support** - Use `--start-season` and `--end-season` instead of listing individual seasons
- **Explicit Season Testing** - Verify that explicitly specifying seasons (e.g., `25-26`) works correctly

---

## 🚀 Setup

### 1. Install Dependencies

```bash
cd /Users/aaryn/swimming/swim-data-tool

# Install the package in development mode (using uv)
uv pip install -e .

# Install MaxPreps dependencies (using uv)
uv pip install playwright beautifulsoup4
playwright install chromium
```

### 2. Check for Syntax Errors

```bash
# Run linter on new files
python -m py_compile src/swim_data_tool/sources/base.py
python -m py_compile src/swim_data_tool/sources/factory.py
python -m py_compile src/swim_data_tool/sources/usa_swimming.py
python -m py_compile src/swim_data_tool/sources/maxpreps.py
python -m py_compile src/swim_data_tool/models/canonical.py
python -m py_compile src/swim_data_tool/commands/roster.py
```

---

## 📋 Test 1: USA Swimming Roster (Backwards Compatibility)

**Purpose:** Verify existing USA Swimming workflow still works

### Setup .env
```bash
cd ~/swimming/sahuarita-stingrays-records  # Or your existing project

# Your existing .env should work as-is:
cat .env
# DATA_SOURCE=usa_swimming  (or omit - it defaults)
# USA_SWIMMING_TEAM_CODE=AZ-SHS
# CLUB_NAME=Sahuarita Stingrays
```

### Test Commands

```bash
# Test 1: Roster with default (no --source flag)
swim-data-tool roster

# Expected:
# - Uses USA Swimming (default)
# - Fetches roster
# - Saves to data/lookups/roster-usa-swimming.csv
# - Shows table with PersonKey, Name, Gender, etc.

# Test 2: Roster with explicit --source
swim-data-tool roster --source=usa_swimming

# Expected: Same as above

# Test 3: Roster with seasons
swim-data-tool roster --source=usa_swimming --seasons=2024 --seasons=2023

# Expected: Roster for 2024 and 2023 seasons
```

### ✅ Success Criteria
- [ ] Command runs without errors
- [ ] Roster CSV created at `data/lookups/roster-usa-swimming.csv`
- [ ] Table displays swimmers with PersonKey, FullName, Gender
- [ ] Output matches previous behavior (backwards compatible)

---

## 📋 Test 2: MaxPreps Roster (New Functionality)

**Purpose:** Verify MaxPreps scraping works

### Setup .env
```bash
cd ~/swimming/tanque-verde

# Create .env with MaxPreps config:
cat > .env << 'EOF'
DATA_SOURCE=maxpreps
MAXPREPS_SCHOOL_SLUG=tanque-verde-hawks
MAXPREPS_STATE=az
MAXPREPS_CITY=tucson
MAXPREPS_SEASONS=24-25
CLUB_NAME=Tanque Verde High School
EOF
```

### Test Commands

```bash
# Test 1: Fetch MaxPreps roster
swim-data-tool roster --source=maxpreps

# Expected:
# - Scrapes MaxPreps website
# - Fetches boys roster (14 swimmers)
# - Fetches girls roster (0 swimmers)
# - Saves to data/lookups/roster-maxpreps.csv
# - Shows table with careerid, Name, Gender, Grade

# Test 2: Multiple seasons
swim-data-tool roster --source=maxpreps --seasons=24-25 --seasons=23-24

# Expected: Roster for both seasons, deduplicated by careerid
```

### ✅ Success Criteria
- [ ] Playwright launches headless browser
- [ ] Scrapes https://www.maxpreps.com/.../roster/ pages
- [ ] Extracts athlete names, careerids, grades
- [ ] Boys and girls rosters scraped separately
- [ ] CSV created at `data/lookups/roster-maxpreps.csv`
- [ ] Table shows: ID (careerid), Name, Gender, Grade, Season
- [ ] Grade levels extracted correctly (Fr., So., Jr., Sr.)

### 📊 Expected Output

```
🏊 Fetching Roster
Data source: MaxPreps

Team: Tanque Verde High School
Team ID: tanque-verde-hawks
Seasons: 24-25

  Fetching boys roster: 24-25
    Found 14 athletes
  Fetching girls roster: 24-25
    No roster table found for girls

✓ Found 14 swimmers
✓ Gender data: 14 males, 0 females

┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ ID           ┃ Name            ┃ Gender ┃ Grade ┃ Season ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ ri9tgoko6... │ Grayson The     │   M    │  Jr.  │ 24-25  │
│ 2phhf4vm3... │ Carter Caball.. │   M    │  Jr.  │ 24-25  │
│ 9cde7152a... │ Lucas Soeder    │   M    │  Sr.  │ 24-25  │
│ 10aavdb9t... │ Wade Olsson     │   M    │  So.  │ 24-25  │
└──────────────┴─────────────────┴────────┴───────┴────────┘

✓ Saved roster to: data/lookups/roster-maxpreps.csv
```

---

## 📋 Test 3: Season Range Testing

**Purpose:** Verify season range feature works correctly for MaxPreps

### Setup
```bash
cd ~/swimming/tanque-verde

# Use the existing .env from Test 2
```

### Test Commands

```bash
# Test 1: Single explicit season (verify 25-26 works)
uv run swim-data-tool roster --source=maxpreps --seasons=25-26

# Expected:
# - Scrapes only 25-26 season (fall 2025)
# - Works correctly with explicit future season

# Test 2: Season range (12-13 to 24-25)
uv run swim-data-tool roster --source=maxpreps --start-season=12-13 --end-season=24-25

# Expected:
# - Expands range to: 12-13, 13-14, 14-15, ..., 23-24, 24-25
# - Shows: "Seasons: 12-13 to 24-25 (13 seasons)"
# - Scrapes all 13 seasons (boys + girls each)
# - Deduplicates by careerid (keeps most recent grade)

# Test 3: Smaller range (22-23 to 24-25)
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25

# Expected:
# - Expands to: 22-23, 23-24, 24-25
# - Shows: "Seasons: 22-23 to 24-25 (3 seasons)"
# - Faster collection (only 3 seasons)

# Test 4: Error handling (only start-season provided)
uv run swim-data-tool roster --source=maxpreps --start-season=22-23

# Expected:
# - Error: "Both --start-season and --end-season must be provided together"

# Test 5: Error handling (only end-season provided)
uv run swim-data-tool roster --source=maxpreps --end-season=24-25

# Expected:
# - Error: "Both --start-season and --end-season must be provided together"
```

### ✅ Success Criteria
- [ ] Single explicit season (25-26) works correctly
- [ ] Season range correctly expands YY-YY format
- [ ] Shows season count: "Seasons: XX-XX to YY-YY (N seasons)"
- [ ] All seasons in range are scraped
- [ ] Deduplication by careerid works across seasons
- [ ] Error when only one range parameter provided
- [ ] Results saved to `data/lookups/roster-maxpreps.csv`

### 📊 Expected Output (Season Range)

```
🏊 Fetching Roster
Data source: MaxPreps

Team: Tanque Verde High School
Team ID: tanque-verde-hawks
Seasons: 22-23 to 24-25 (3 seasons)

  Fetching boys roster: 22-23
    Found 10 athletes
  Fetching girls roster: 22-23
    No roster table found for girls
  Fetching boys roster: 23-24
    Found 12 athletes
  Fetching girls roster: 23-24
    No roster table found for girls
  Fetching boys roster: 24-25
    Found 14 athletes
  Fetching girls roster: 24-25
    No roster table found for girls

✓ Found 14 swimmers (deduplicated by careerid)
✓ Gender data: 14 males, 0 females

┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━┓
┃ ID           ┃ Name            ┃ Gender ┃ Grade ┃ Season ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━┩
│ ri9tgoko6... │ Grayson The     │   M    │  Jr.  │ 24-25  │
│ 2phhf4vm3... │ Carter Caball.. │   M    │  Jr.  │ 24-25  │
│ 9cde7152a... │ Lucas Soeder    │   M    │  Sr.  │ 24-25  │
│ 10aavdb9t... │ Wade Olsson     │   M    │  So.  │ 24-25  │
└──────────────┴─────────────────┴────────┴───────┴────────┘

✓ Saved roster to: data/lookups/roster-maxpreps.csv
```

**Note:** Swimmers appear with their most recent grade (24-25 season) due to deduplication

---

## 📋 Test 4: Python Module Testing

### Test Source Factory

```bash
cd /Users/aaryn/swimming/swim-data-tool

# Test in Python REPL
python3 << 'EOF'
from swim_data_tool.sources.factory import list_sources, get_source

# List available sources
print("Available sources:", list_sources())
# Expected: ['maxpreps', 'usa_swimming']

# Get USA Swimming source
source = get_source("usa_swimming")
print(f"Source name: {source.source_name}")
print(f"ID field: {source.swimmer_id_field}")
# Expected: Source name: USA Swimming, ID field: PersonKey

# Get MaxPreps source
source = get_source("maxpreps")
print(f"Source name: {source.source_name}")
print(f"ID field: {source.swimmer_id_field}")
# Expected: Source name: MaxPreps, ID field: careerid

print("✓ Source factory working!")
EOF
```

### Test Canonical Data Models

```bash
python3 << 'EOF'
from swim_data_tool.models.canonical import Swimmer, Swim, validate_canonical_dataframe
import pandas as pd

# Create test swimmer
swimmer = Swimmer(
    swimmer_id="123",
    full_name="Test Swimmer",
    gender="M",
    grade="10",
    source="maxpreps"
)
print(f"Swimmer: {swimmer.full_name}, Grade: {swimmer.grade}")

# Test DataFrame validation
df = pd.DataFrame([{
    "swimmer_id": "123",
    "swimmer_name": "Test",
    "gender": "M",
    "age": 15,
    "event_code": "50-free",
    "time": "21.45",
    "time_seconds": 21.45,
    "swim_date": "2024-10-01",
    "meet": "Test Meet",
    "source": "maxpreps"
}])

is_valid, errors = validate_canonical_dataframe(df)
print(f"DataFrame valid: {is_valid}")
if errors:
    print(f"Errors: {errors}")

print("✓ Canonical models working!")
EOF
```

---

## 🐛 Common Issues & Fixes

### Issue 1: Playwright not installed
```
Error: playwright is required for MaxPreps source
```
**Fix:**
```bash
pip install playwright
playwright install chromium
```

### Issue 2: Module not found
```
ModuleNotFoundError: No module named 'swim_data_tool.sources'
```
**Fix:**
```bash
cd /Users/aaryn/swimming/swim-data-tool
pip install -e .
```

### Issue 3: MaxPreps timeout
```
TimeoutError: Page.goto: Timeout 60000ms exceeded
```
**Fix:**
- Check internet connection
- Try again (MaxPreps might be slow)
- Increase timeout in maxpreps.py if persistent

### Issue 4: BeautifulSoup not found
```
ModuleNotFoundError: No module named 'bs4'
```
**Fix:**
```bash
pip install beautifulsoup4
```

---

## 📊 Test Results Template

### USA Swimming Roster Test
- [ ] Command executed: `swim-data-tool roster`
- [ ] No errors
- [ ] CSV created: `data/lookups/roster-usa-swimming.csv`
- [ ] Roster count matches expected
- [ ] Table displayed correctly
- [ ] Gender data shown

### MaxPreps Roster Test  
- [ ] Command executed: `swim-data-tool roster --source=maxpreps`
- [ ] Playwright launched
- [ ] Boys roster scraped successfully
- [ ] Girls roster scraped (or no data message)
- [ ] CSV created: `data/lookups/roster-maxpreps.csv`
- [ ] Grade levels extracted (Fr./So./Jr./Sr.)
- [ ] Table displayed correctly

### Module Tests
- [ ] Source factory loads both sources
- [ ] Can instantiate USA Swimming source
- [ ] Can instantiate MaxPreps source
- [ ] Canonical data models work
- [ ] DataFrame validation works

---

## 🎯 What to Report

If testing, please report:

1. **Which tests passed/failed**
2. **Any error messages** (full traceback)
3. **CSV file contents** (first few rows)
4. **Python version** (`python --version`)
5. **OS** (macOS, Linux, Windows)

---

## 📝 Next Steps After Testing

Once roster command is verified:
1. Update import_swimmers command (TODO #8)
2. Test full MaxPreps workflow (roster → import → records)
3. Implement grade-based records (TODO #11)

---

**Happy Testing!** 🧪🏊

