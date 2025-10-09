# CLI Workflow: Multi-Source Architecture

**Date:** October 8, 2025  
**Goal:** Show command-line workflow for USA Swimming vs MaxPreps

---

## 🎯 Design Principle

**Default to USA Swimming for backwards compatibility**
- No `--source` flag = USA Swimming (existing behavior)
- `--source=maxpreps` = Use MaxPreps instead
- Configuration in `.env` provides defaults

---

## 📋 USA Swimming Workflow (Current - Default)

### Step 1: Initialize Project
```bash
$ swim-data-tool init
```

### Step 2: Configure `.env`
```bash
# Data source (optional - defaults to usa_swimming)
DATA_SOURCE=usa_swimming

# USA Swimming configuration
USA_SWIMMING_TEAM_ID=AZ-SHS
USA_SWIMMING_TEAM_NAMES=Sahuarita Stingrays,Sahuarita Stingrays Swim Club
START_YEAR=1998
END_YEAR=2024

# Team info
CLUB_NAME=Sahuarita Stingrays
```

### Step 3: Get Team Roster
```bash
# Fetch roster from USA Swimming
$ swim-data-tool roster

# Or explicitly specify source
$ swim-data-tool roster --source=usa_swimming

# Output: data/lookups/roster.csv
# Columns: PersonKey, FullName, Gender, Age, TeamName
```

### Step 4: Import Swimmer Data
```bash
# Download all swimmers from roster
$ swim-data-tool import swimmers

# Or explicitly specify source
$ swim-data-tool import swimmers --source=usa_swimming

# Output: data/raw/swimmers/*.csv (one per swimmer)
```

### Step 5: Classify Unattached Swims
```bash
$ swim-data-tool classify unattached

# Output: data/processed/unattached/probationary/*.csv
```

### Step 6: Generate Records
```bash
# Generate all courses
$ swim-data-tool generate records

# Or specific course
$ swim-data-tool generate records --course=scy

# Output: 
#   data/records/scy/records-boys.md
#   data/records/scy/records-girls.md
#   data/records/lcm/records-boys.md
#   data/records/lcm/records-girls.md
```

### Step 7: Generate Top 10 Lists
```bash
$ swim-data-tool generate top10

# Output: data/records/top10/scy/{event}.md
```

### Step 8: Generate Annual Summary
```bash
$ swim-data-tool generate annual --season=2024

# Output: data/records/annual/2024-scy-boys.md
```

### Step 9: Publish
```bash
$ swim-data-tool publish

# Pushes records to public GitHub repo (no PII)
```

---

## 🏫 MaxPreps Workflow (New)

### Step 1: Initialize Project
```bash
$ swim-data-tool init --source=maxpreps

# Creates .env with MaxPreps template
```

### Step 2: Configure `.env`
```bash
# Data source
DATA_SOURCE=maxpreps

# MaxPreps configuration
MAXPREPS_SCHOOL_SLUG=tanque-verde-hawks
MAXPREPS_STATE=az
MAXPREPS_CITY=tucson
MAXPREPS_SEASONS=24-25,23-24,22-23

# Team info
CLUB_NAME=Tanque Verde High School
```

### Step 3: Get Team Roster
```bash
# Fetch roster from MaxPreps (boys + girls)
$ swim-data-tool roster --source=maxpreps

# Or use default from .env
$ swim-data-tool roster

# Output: data/lookups/roster-maxpreps.csv
# Columns: careerid, swimmer_name, gender, grade, school_name
```

### Step 4: Import Swimmer Data
```bash
# Scrape all swimmer pages from roster
$ swim-data-tool import swimmers --source=maxpreps

# Or use default from .env
$ swim-data-tool import swimmers

# Output: data/raw/swimmers/*.csv (one per swimmer)
# Format: Canonical format (same columns as USA Swimming after normalization)
```

### Step 5: Generate Records
```bash
# Generate all courses (same command!)
$ swim-data-tool generate records

# Output: 
#   data/records/scy/records-boys.md
#   data/records/scy/records-girls.md
```

### Step 6: Generate Top 10 Lists (Same!)
```bash
$ swim-data-tool generate top10
```

### Step 7: Generate Annual Summary (Same!)
```bash
$ swim-data-tool generate annual --season=2024
```

### Step 8: Publish (Same!)
```bash
$ swim-data-tool publish
```

---

## 🔄 Mixed Source Workflow (Advanced)

### Scenario: Club swimmer who also swims high school

**Option 1: Separate Repositories**
```bash
# Club records (USA Swimming)
cd ~/club-records
swim-data-tool roster --source=usa_swimming
swim-data-tool import swimmers --source=usa_swimming
swim-data-tool generate records

# High school records (MaxPreps)
cd ~/hs-records
swim-data-tool roster --source=maxpreps
swim-data-tool import swimmers --source=maxpreps
swim-data-tool generate records
```

**Option 2: Combined Repository (Future Feature)**
```bash
# Get data from both sources
$ swim-data-tool roster --source=usa_swimming
$ swim-data-tool roster --source=maxpreps

# Import from both
$ swim-data-tool import swimmers --source=usa_swimming
$ swim-data-tool import swimmers --source=maxpreps

# Generate combined records
$ swim-data-tool generate records --combined

# Output: Unified records with source attribution
```

---

## 📝 Detailed Command Reference

### `swim-data-tool init`

**Purpose:** Initialize new project

**Flags:**
- `--source=<source>` - Specify data source for .env template (default: usa_swimming)

**Examples:**
```bash
$ swim-data-tool init                    # USA Swimming template
$ swim-data-tool init --source=maxpreps  # MaxPreps template
```

---

### `swim-data-tool roster`

**Purpose:** Fetch team roster from data source

**Flags:**
- `--source=<source>` - Override data source (default: from .env or usa_swimming)
- `--seasons=<season>` - Comma-separated seasons (e.g., 2024,2023,2022)

**Examples:**
```bash
# USA Swimming (default)
$ swim-data-tool roster
$ swim-data-tool roster --source=usa_swimming
$ swim-data-tool roster --source=usa_swimming --seasons=2024,2023

# MaxPreps
$ swim-data-tool roster --source=maxpreps
$ swim-data-tool roster --source=maxpreps --seasons=24-25,23-24
```

**Output:**
- USA Swimming: `data/lookups/roster.csv` or `data/lookups/roster-usa-swimming.csv`
- MaxPreps: `data/lookups/roster-maxpreps.csv`

---

### `swim-data-tool import swimmers`

**Purpose:** Download/scrape swimmer data

**Flags:**
- `--source=<source>` - Override data source (default: from .env)
- `--file=<csv>` - Roster CSV (default: data/lookups/roster.csv or roster-{source}.csv)
- `--dry-run` - Show what would be downloaded without downloading
- `--force` - Re-download all swimmers (ignore cache)

**Examples:**
```bash
# USA Swimming (default)
$ swim-data-tool import swimmers
$ swim-data-tool import swimmers --source=usa_swimming
$ swim-data-tool import swimmers --dry-run

# MaxPreps
$ swim-data-tool import swimmers --source=maxpreps
$ swim-data-tool import swimmers --source=maxpreps --dry-run
$ swim-data-tool import swimmers --source=maxpreps --force

# Custom roster file
$ swim-data-tool import swimmers --file=data/custom-roster.csv
```

**Output:**
- `data/raw/swimmers/*.csv` (one per swimmer, canonical format)

---

### `swim-data-tool generate records`

**Purpose:** Generate team records (source-agnostic!)

**Flags:**
- `--course=<course>` - Specific course (scy, lcm, scm) or all (default: all)

**Examples:**
```bash
$ swim-data-tool generate records              # All courses
$ swim-data-tool generate records --course=scy  # SCY only
```

**Output:**
- `data/records/scy/records-boys.md`
- `data/records/scy/records-girls.md`
- `data/records/lcm/records-boys.md`
- etc.

**Note:** No `--source` flag needed! Works with data from ANY source.

---

### `swim-data-tool generate top10`

**Purpose:** Generate top 10 all-time lists (source-agnostic!)

**Flags:**
- `--course=<course>` - Specific course or all (default: all)
- `--n=<number>` - Number of swimmers (default: 10)

**Examples:**
```bash
$ swim-data-tool generate top10           # Top 10, all courses
$ swim-data-tool generate top10 --n=25    # Top 25
$ swim-data-tool generate top10 --course=scy --n=50  # Top 50 SCY
```

---

### `swim-data-tool generate annual`

**Purpose:** Generate annual season summary (source-agnostic!)

**Flags:**
- `--season=<year>` - Season year (e.g., 2024)
- `--course=<course>` - Specific course or all (default: all)

**Examples:**
```bash
$ swim-data-tool generate annual --season=2024
$ swim-data-tool generate annual --season=2023 --course=scy
```

---

### `swim-data-tool status`

**Purpose:** Show current configuration and data status

**Flags:**
- None

**Example:**
```bash
$ swim-data-tool status

📊 Swim Data Tool Status

Data Source: MaxPreps
Team: Tanque Verde High School
Location: Tucson, AZ

Configuration:
  School: tanque-verde-hawks
  Seasons: 24-25, 23-24, 22-23

Data Summary:
  Swimmers: 14 (cached)
  Total swims: 1,247
  Date range: 2022-09-01 to 2024-11-15

Records Generated:
  ✓ SCY records (boys/girls)
  ✓ LCM records (boys/girls)
  ✓ Top 10 lists (22 events)
  ✓ 2024 annual summary

Last updated: 2025-10-08 14:23:45
```

---

## 🔧 Configuration Comparison

### `.env` for USA Swimming
```bash
# Data source
DATA_SOURCE=usa_swimming

# USA Swimming API
USA_SWIMMING_TEAM_ID=AZ-SHS
USA_SWIMMING_TEAM_NAMES=Sahuarita Stingrays,Sahuarita Stingrays Swim Club
START_YEAR=1998
END_YEAR=2024

# Team info
CLUB_NAME=Sahuarita Stingrays

# Optional: Publishing
PUBLIC_REPO_URL=https://github.com/user/sahuarita-stingrays-records.git
PUBLIC_REPO_LOCAL=/tmp/sahuarita-records
```

### `.env` for MaxPreps
```bash
# Data source
DATA_SOURCE=maxpreps

# MaxPreps
MAXPREPS_SCHOOL_SLUG=tanque-verde-hawks
MAXPREPS_STATE=az
MAXPREPS_CITY=tucson
MAXPREPS_SEASONS=24-25,23-24,22-23,21-22

# Team info
CLUB_NAME=Tanque Verde High School

# Optional: Publishing
PUBLIC_REPO_URL=https://github.com/user/tanque-verde-records.git
PUBLIC_REPO_LOCAL=/tmp/tanque-verde-records
```

---

## 🎯 User Experience Goals

### 1. **Backwards Compatible**
Existing USA Swimming users see **no changes**:
```bash
$ swim-data-tool roster          # Still works!
$ swim-data-tool import swimmers  # Still works!
$ swim-data-tool generate records # Still works!
```

### 2. **Explicit Override**
Can always override with `--source`:
```bash
$ swim-data-tool roster --source=usa_swimming
$ swim-data-tool roster --source=maxpreps
```

### 3. **Configuration-Driven**
Set once in `.env`, forget it:
```bash
# Set in .env
DATA_SOURCE=maxpreps

# Then just use normal commands
$ swim-data-tool roster
$ swim-data-tool import swimmers
```

### 4. **Source-Agnostic Processing**
Record generation commands are **identical** regardless of source:
```bash
# Works with USA Swimming data
$ swim-data-tool generate records

# Works with MaxPreps data
$ swim-data-tool generate records

# Works with ANY source data!
```

---

## 🚀 Migration Path

### Existing USA Swimming Users

**No changes required!** Existing workflows continue to work:

```bash
# Before refactoring
$ swim-data-tool roster
$ swim-data-tool import swimmers
$ swim-data-tool generate records

# After refactoring (identical)
$ swim-data-tool roster
$ swim-data-tool import swimmers
$ swim-data-tool generate records
```

**Optional:** Add `DATA_SOURCE=usa_swimming` to `.env` for explicitness.

### New MaxPreps Users

```bash
# 1. Initialize
$ swim-data-tool init --source=maxpreps

# 2. Edit .env with your school info
$ vim .env

# 3. Use same commands as USA Swimming
$ swim-data-tool roster
$ swim-data-tool import swimmers
$ swim-data-tool generate records
```

---

## 📊 Command Comparison Matrix

| Command | USA Swimming | MaxPreps | Notes |
|---------|--------------|----------|-------|
| `init` | ✅ | ✅ | Add `--source=maxpreps` |
| `roster` | ✅ | ✅ | Add `--source=maxpreps` |
| `import swimmers` | ✅ | ✅ | Add `--source=maxpreps` |
| `classify unattached` | ✅ | ⚠️ | MaxPreps: N/A (all swims are "team") |
| `generate records` | ✅ | ✅ | **Identical - no source flag** |
| `generate top10` | ✅ | ✅ | **Identical - no source flag** |
| `generate annual` | ✅ | ✅ | **Identical - no source flag** |
| `publish` | ✅ | ✅ | **Identical - no source flag** |
| `status` | ✅ | ✅ | Shows current source |

---

## 🎬 Complete Example: New MaxPreps User

```bash
# 1. Install
$ pip install swim-data-tool

# 2. Create project directory
$ mkdir tanque-verde-records
$ cd tanque-verde-records

# 3. Initialize with MaxPreps
$ swim-data-tool init --source=maxpreps

✅ Created .env (edit with your school info)
✅ Created data/ directory structure

Next steps:
  1. Edit .env with your MaxPreps school slug
  2. Run: swim-data-tool roster --source=maxpreps

# 4. Edit .env
$ vim .env
# Set:
#   MAXPREPS_SCHOOL_SLUG=tanque-verde-hawks
#   MAXPREPS_STATE=az
#   MAXPREPS_CITY=tucson
#   CLUB_NAME=Tanque Verde High School

# 5. Get roster
$ swim-data-tool roster --source=maxpreps

🏊 Fetching MaxPreps Roster
  School: tanque-verde-hawks (Tucson, AZ)
  Seasons: 24-25

📥 Scraping boys roster...
  Found: 14 swimmers

📥 Scraping girls roster...
  Found: 0 swimmers

✅ Saved roster: data/lookups/roster-maxpreps.csv
  Total swimmers: 14

# 6. Import swimmer data
$ swim-data-tool import swimmers --source=maxpreps

🏊 Import Swimmers
  CSV File: data/lookups/roster-maxpreps.csv
  Total swimmers: 14
  Output: data/raw/swimmers

📥 Scraping swimmer pages...
[██████████] 14/14 (100%) - Zachary Duerkop

✅ Import Complete!
  Downloaded: 14 swimmers
  No data: 0 swimmers

# 7. Generate records
$ swim-data-tool generate records

🏊 Generating Team Records

📂 Loading swimmer data...
✓ Loaded 247 swims

🔍 Filtering team swims...
✓ Found 247 team swims

⚙️ Parsing events...
✓ Parsed events

📊 Generating SCY records...
  ✓ Boys: 156 records
    Generated: data/records/scy/records-boys.md

✓ Record Generation Complete!

# 8. View records
$ cat data/records/scy/records-boys.md

# Tanque Verde High School - Boys
## Team Records - Short Course Yards (SCY)

### 50 Freestyle
| Age Group | Time | Athlete | Age | Date | Meet |
|-----------|------|---------|-----|------|------|
| 15-16 | 24.02 | Jackson Eftekhar | 15 | 9/20/2024 | CDO Classic |
| Open | 24.02 | Jackson Eftekhar | 15 | 9/20/2024 | CDO Classic |

### 100 Freestyle
| Age Group | Time | Athlete | Age | Date | Meet |
|-----------|------|---------|-----|------|------|
| 15-16 | 50.64 | Zachary Duerkop | 16 | 11/9/2024 | State Championships |
...

# 9. Publish (optional)
$ swim-data-tool publish

📤 Publishing records to GitHub...
✅ Published to: github.com/user/tanque-verde-records

Done! 🎉
```

---

## 💡 Key Takeaways

### For Users
1. **Default behavior unchanged** - USA Swimming users see no difference
2. **Explicit override** - Use `--source=maxpreps` when needed
3. **Configuration-driven** - Set `DATA_SOURCE` in `.env` once
4. **Source-agnostic processing** - Record generation is identical

### For Developers
1. **Plugin architecture** - Easy to add new sources
2. **Minimal code duplication** - 85% of code is reused
3. **Clear separation** - Data collection vs. record generation
4. **Backwards compatible** - No breaking changes

---

**Last Updated:** October 8, 2025  
**Status:** Design complete, ready for implementation  
**Next:** Build source plugin system


