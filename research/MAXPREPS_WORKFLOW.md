# MaxPreps Workflow

**Date:** October 8, 2025  
**Version:** 0.10.0

---

## 🎯 Complete MaxPreps Workflow

This is the **simplified workflow** for high school teams using MaxPreps. No "classify" step needed!

---

## 📋 Step-by-Step

### 1. Initialize Repository
```bash
cd ~/swimming/your-school-name
uv run swim-data-tool init "Your High School Name"

# Select: 2. MaxPreps (high school)
# Provide: school slug, state, city, season
```

### 2. Fetch Team Roster
```bash
# Single season
uv run swim-data-tool roster --source=maxpreps

# Multiple seasons (recommended)
uv run swim-data-tool roster --source=maxpreps --start-season=20-21 --end-season=24-25

# Or specific seasons
uv run swim-data-tool roster --source=maxpreps --seasons=23-24 --seasons=24-25
```

**Output:** `data/lookups/roster-maxpreps.csv` with athlete names, careerids, and grades

### 3. Import Swimmer Data
```bash
uv run swim-data-tool import swimmers --source=maxpreps
```

**Output:** Individual CSV files in `data/raw/swimmers/` with all swim times

### 4. Generate Records
```bash
uv run swim-data-tool generate records
```

**Output:** Records organized by grade level:
- `data/records/scy/open/` - All grades combined
- `data/records/scy/freshman/` - 9th grade only
- `data/records/scy/sophomore/` - 10th grade only
- `data/records/scy/junior/` - 11th grade only
- `data/records/scy/senior/` - 12th grade only

---

## ⚠️ What's Different from USA Swimming?

### No "Classify" Step ❌
MaxPreps teams don't have "unattached" swims, so you **skip** this step:
```bash
# NOT NEEDED for MaxPreps
# swim-data-tool classify unattached  ← Skip this!
```

### Grade-Based Records ✅
Records are grouped by **grade level** (Freshman, Sophomore, Junior, Senior) instead of age groups.

### Web Scraping Speed 🐢
MaxPreps uses web scraping, so imports are slower (~1-2 seconds per swimmer) compared to USA Swimming API calls.

---

## 🎓 Record Categories

### Open (All Grades)
Best times across all grade levels - these are your school's all-time records.

### By Grade Level
- **Freshman** (9th grade) - Best times by freshmen
- **Sophomore** (10th grade) - Best times by sophomores
- **Junior** (11th grade) - Best times by juniors
- **Senior** (12th grade) - Best times by seniors

This lets you see:
- School progression (how swimmers improve each year)
- Grade-level comparison
- Historical context (comparing this year's sophomores to past sophomores)

---

## 📊 Example: Tanque Verde High School

```bash
cd ~/swimming/tanque-verde

# Step 1: Already initialized ✅

# Step 2: Fetch roster (3 seasons)
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25

# Step 3: Import swimmers (14 athletes)
uv run swim-data-tool import swimmers --source=maxpreps

# Step 4: Generate records
uv run swim-data-tool generate records

# View records
ls -R data/records/scy/
# open/
# freshman/
# sophomore/
# junior/
# senior/
```

---

## ✅ Success Indicators

After completing all steps:

- ✅ Roster CSV has athlete names and grades
- ✅ Each swimmer has a CSV in `data/raw/swimmers/`
- ✅ Records generated in `data/records/scy/`
- ✅ Separate directories for each grade level
- ✅ Open records show best times across all grades

---

## 🔄 Updating Records

To update records with new season data:

```bash
# Add new season to roster
uv run swim-data-tool roster --source=maxpreps --seasons=25-26

# Import new swimmers (or re-import with --force)
uv run swim-data-tool import swimmers --source=maxpreps --force

# Regenerate records
uv run swim-data-tool generate records
```

---

## 🆚 USA Swimming vs MaxPreps Comparison

| Step | USA Swimming | MaxPreps |
|------|--------------|----------|
| **Init** | Team code + LSC | School slug + location |
| **Roster** | `--seasons=all` | `--start-season=XX-XX --end-season=YY-YY` |
| **Import** | API (fast) | Web scraping (slower) |
| **Classify** | ✅ Required | ❌ Not needed |
| **Records** | Age groups | Grade levels + Open |

---

## 📚 Related Documentation

- `MAXPREPS_RECORDS_PLAN.md` - Grade-based record implementation
- `SEASON_RANGE_COMPLETE.md` - Season range feature
- `TESTING.md` - Full test suite

---

**3 Simple Steps:** Roster → Import → Records! 🚀


