# Generalization Analysis: Multi-Source Record Generation

**Date:** October 8, 2025  
**Purpose:** Identify components of USA Swimming workflow that can be generalized for MaxPreps and other sources

---

## 🔍 Current USA Swimming Workflow

### Step 1: Data Collection
```
roster.csv (PersonKey, FullName, Gender) 
    ↓
import swimmers (API calls)
    ↓
data/raw/swimmers/*.csv (one per swimmer)
```

### Step 2: Data Processing
```
Load all swimmer CSVs
    ↓
Filter team swims (by team name)
    ↓
Parse events (50 FR SCY → 50-free, scy)
    ↓
Normalize times (1:42.15 → 102.15 seconds)
    ↓
Determine age groups (15 → "15-16")
```

### Step 3: Record Generation
```
Get best times by event/age group/course
    ↓
Generate markdown tables
    ↓
Output: data/records/scy/records-boys.md
```

---

## ✅ Source-Agnostic Components (100% Reusable)

These components work with ANY data source after normalization:

### 1. Event Definitions (`models/events.py`)

**What it does:**
- Defines standard event codes (`50-free`, `100-back`, etc.)
- Defines age groups (`10U`, `11-12`, `13-14`, etc.)
- Defines courses (`SCY`, `LCM`, `SCM`)
- Parses events into components
- Converts times to seconds for sorting
- Formats event names for display

**Why it's reusable:**
- Events are universal (50 free is 50 free regardless of source)
- Age groups are standard (USA Swimming convention)
- Time formats are consistent

**Example:**
```python
# Works for ANY source
convert_time_to_seconds("1:42.15")  # → 102.15
determine_age_group(15)  # → "15-16"
format_event_name("50-free")  # → "50 Freestyle"
```

**MaxPreps compatibility:** ✅ 100% compatible

---

### 2. Record Generation Logic (`services/record_generator.py`)

**Core functions that are source-agnostic:**

#### `get_best_times_by_event(df, course)`
- Input: Normalized DataFrame with standard columns
- Process: Group by event/age group, find fastest time
- Output: `{event_code: {age_group: RecordEntry}}`
- **Works with any source if DataFrame has standard columns**

#### `get_top_n_by_event(df, course, n=10)`
- Input: Normalized DataFrame
- Process: Sort by time, take top N (no age group filtering)
- Output: List of top N times per event
- **Works with any source**

#### `filter_by_gender(df, gender)`
- Input: DataFrame with `Gender` column
- Output: Filtered DataFrame for M or F
- **Works with any source**

#### `filter_by_season(df, season)`
- Input: DataFrame with `SwimDate` column
- Output: Filtered DataFrame for year
- **Works with any source**

#### `generate_records_markdown(records, course, team_name, output_path)`
- Input: Records dict (from get_best_times_by_event)
- Process: Format as markdown tables
- Output: Markdown file
- **Completely source-agnostic**

**Why it's reusable:**
- Operates on normalized DataFrames (standard columns)
- Doesn't care WHERE data came from
- Pure data transformation logic

**MaxPreps compatibility:** ✅ 100% compatible (after normalization)

---

### 3. Output Generation

All markdown generation functions are source-agnostic:
- `generate_records_markdown()` - Team records by age group
- `generate_top10_markdown()` - Top N all-time lists
- `generate_annual_summary_markdown()` - Season summaries

**These don't care about the data source at all!**

---

### 4. Time Parsing & Normalization

```python
# Universal time parsing
convert_time_to_seconds("21.45")    # → 21.45
convert_time_to_seconds("1:42.15")  # → 102.15
convert_time_to_seconds("15:42.10") # → 942.10
```

**Works for:**
- USA Swimming format
- MaxPreps format
- Any MM:SS.SS or SS.SS format

---

## 🔄 Components That Need Abstraction

These components are currently USA Swimming-specific but can be abstracted:

### 1. Data Source Layer

**Current (USA Swimming-specific):**
```python
class USASwimmingAPI:
    def get_team_roster(team_id, seasons):
        # Sisense API calls
        # Returns: PersonKey, FullName, Gender
    
    def download_swimmer_career(person_key, start_year, end_year):
        # Sisense API calls
        # Returns: DataFrame with Event, SwimTime, Age, SwimDate, etc.
```

**Generalized Interface:**
```python
class SwimDataSource(ABC):
    """Abstract base class for swim data sources"""
    
    @abstractmethod
    def get_team_roster(self, team_id: str, seasons: List[str]) -> pd.DataFrame:
        """Get team roster
        
        Returns DataFrame with standard columns:
        - swimmer_id: Unique identifier (PersonKey, careerid, etc.)
        - swimmer_name: Full name
        - gender: M or F
        - grade: Optional grade level
        """
        pass
    
    @abstractmethod
    def get_swimmer_history(self, swimmer_id: str) -> pd.DataFrame:
        """Get all swims for a swimmer
        
        Returns DataFrame with standard columns:
        - swimmer_id
        - swimmer_name
        - event: Event string (will be parsed)
        - time: Formatted time string
        - age: Age at swim
        - date: Swim date (YYYY-MM-DD or MM/DD/YYYY)
        - meet: Meet name
        - gender: M or F
        - source: Source identifier
        """
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable source name"""
        pass
```

**Implementations:**

```python
class USASwimmingSource(SwimDataSource):
    source_name = "USA Swimming"
    
    def get_team_roster(self, team_id, seasons):
        # Call Sisense API
        # Return standardized DataFrame
        pass
    
    def get_swimmer_history(self, swimmer_id):
        # PersonKey → API call
        # Return standardized DataFrame
        pass

class MaxPrepsSource(SwimDataSource):
    source_name = "MaxPreps"
    
    def get_team_roster(self, school_slug, seasons):
        # Scrape roster pages (boys + girls)
        # Return standardized DataFrame
        pass
    
    def get_swimmer_history(self, careerid):
        # Scrape athlete stats page
        # Return standardized DataFrame
        pass
```

---

### 2. Canonical Data Format

**Standard DataFrame columns (after normalization):**

| Column | Type | Description | USA Swimming | MaxPreps |
|--------|------|-------------|--------------|----------|
| `swimmer_id` | str | Unique ID | PersonKey | careerid |
| `swimmer_name` | str | Full name | Name | careerName |
| `gender` | str | M or F | Gender | gender from metadata |
| `age` | int | Age at swim | Age | Calculate from metadata |
| `grade` | str | Grade (optional) | — | grade from metadata |
| `event_distance` | str | Distance (50, 100, etc.) | Parsed | Parsed |
| `event_stroke` | str | Stroke (free, back, etc.) | Parsed | Parsed |
| `event_course` | str | Course (scy, lcm, scm) | Parsed | Parsed |
| `event_code` | str | Normalized (50-free) | Created | Created |
| `time` | str | Formatted time | SwimTime | time from HTML |
| `time_seconds` | float | For sorting | Calculated | Calculated |
| `date` | str | Swim date | SwimDate | date (parse format) |
| `meet` | str | Meet name | Meet | meet from HTML |
| `team_name` | str | Team/school | Team | schoolName |
| `source` | str | Data source | "usa_swimming" | "maxpreps" |
| `source_url` | str | Source URL | API endpoint | Athlete URL |

**This is the KEY abstraction!** Once data is in this format, all downstream processing is identical.

---

### 3. Team Identification

**Current (USA Swimming-specific):**
```python
team_names = ["Sahuarita Stingrays", "Sahuarita Stingrays Swim Club"]
df_team = df[df["Team"].str.contains("|".join(team_names))]
```

**Generalized:**
```python
class TeamIdentifier(ABC):
    @abstractmethod
    def is_team_swim(self, swim_row: pd.Series) -> bool:
        pass

class USASwimmingTeamIdentifier(TeamIdentifier):
    def __init__(self, team_names: List[str]):
        self.team_names = team_names
    
    def is_team_swim(self, swim_row):
        return any(name in swim_row["team_name"] for name in self.team_names)

class MaxPrepsTeamIdentifier(TeamIdentifier):
    def __init__(self, school_id: str):
        self.school_id = school_id
    
    def is_team_swim(self, swim_row):
        # MaxPreps: ALL swims from school roster are team swims
        return swim_row.get("school_id") == self.school_id
```

---

### 4. Configuration

**Current (.env for USA Swimming):**
```
USA_SWIMMING_TEAM_ID=AZ-SHS
USA_SWIMMING_TEAM_NAMES=Sahuarita Stingrays,Sahuarita Stingrays Swim Club
START_YEAR=1998
END_YEAR=2024
```

**Generalized:**
```
# Data source selection
DATA_SOURCE=usa_swimming  # or maxpreps

# USA Swimming config
USA_SWIMMING_TEAM_ID=AZ-SHS
USA_SWIMMING_TEAM_NAMES=Sahuarita Stingrays,Sahuarita Stingrays Swim Club
USA_SWIMMING_START_YEAR=1998
USA_SWIMMING_END_YEAR=2024

# MaxPreps config
MAXPREPS_SCHOOL_SLUG=tanque-verde-hawks
MAXPREPS_STATE=az
MAXPREPS_CITY=tucson
MAXPREPS_SEASONS=24-25,23-24,22-23

# Team info (shared)
CLUB_NAME=Tanque Verde High School
```

---

## 🏗️ Proposed Architecture

### Directory Structure
```
swim-data-tool/
├── src/swim_data_tool/
│   ├── sources/              # NEW: Data source plugins
│   │   ├── __init__.py
│   │   ├── base.py           # SwimDataSource abstract class
│   │   ├── usa_swimming.py   # USA Swimming implementation
│   │   ├── maxpreps.py       # MaxPreps implementation
│   │   └── factory.py        # Source factory
│   │
│   ├── models/
│   │   ├── events.py         # ✅ Already source-agnostic
│   │   └── canonical.py      # NEW: Canonical data format
│   │
│   ├── services/
│   │   ├── record_generator.py  # ✅ Already mostly agnostic
│   │   └── normalizer.py        # NEW: Source → Canonical
│   │
│   └── commands/
│       ├── roster.py         # UPDATE: Use source factory
│       ├── import_swimmers.py # UPDATE: Use source factory
│       └── generate.py       # ✅ Already source-agnostic
```

---

## 📋 Refactoring Plan

### Phase 1: Abstract Data Source (Week 1)
1. Create `sources/base.py` with `SwimDataSource` abstract class
2. Move USA Swimming API to `sources/usa_swimming.py`
3. Implement `USASwimmingSource` inheriting from base
4. Create `sources/factory.py` for dynamic source selection
5. Test: Existing USA Swimming workflow still works

### Phase 2: Canonical Data Model (Week 1)
1. Define `models/canonical.py` with standard DataFrame schema
2. Create `services/normalizer.py` to convert source → canonical
3. Update `RecordGenerator` to expect canonical format
4. Test: Generate records from canonical data

### Phase 3: MaxPreps Source (Week 2-3)
1. Implement `sources/maxpreps.py`
2. Roster scraping (boys + girls)
3. Athlete stats scraping
4. Data normalization to canonical format
5. Test: Generate records from MaxPreps data

### Phase 4: Multi-Source Commands (Week 3)
1. Update `roster.py` to use source factory
2. Update `import_swimmers.py` to use source factory
3. Add `--source` flag to commands
4. Update `.env` configuration
5. Test: Switch between USA Swimming and MaxPreps

### Phase 5: Combined Records (Week 4)
1. Merge USA Swimming + MaxPreps data
2. Deduplicate swimmers (name matching)
3. Generate unified records
4. Handle source attribution in output

---

## 🎯 What Stays Exactly the Same

After refactoring, these components need **ZERO changes**:

### ✅ Record Generation (`services/record_generator.py`)
```python
# These functions work with ANY source
get_best_times_by_event(df, course)  # ← df can be from USA Swimming OR MaxPreps
get_top_n_by_event(df, course, n)
filter_by_gender(df, gender)
filter_by_season(df, season)
generate_records_markdown(...)
generate_top10_markdown(...)
```

**No changes needed!** Just feed it canonical DataFrames.

### ✅ Event Definitions (`models/events.py`)
```python
# Universal across all sources
AGE_GROUPS
SCY_EVENTS, LCM_EVENTS, SCM_EVENTS
parse_api_event()
convert_time_to_seconds()
determine_age_group()
```

**No changes needed!** Already source-agnostic.

### ✅ Output Generation
All markdown generation is source-agnostic. Just add source attribution:
```markdown
| Time | Athlete | Age | Date | Meet | Source |
|------|---------|-----|------|------|--------|
| 21.45 | John Doe | 15 | 2024-09-20 | State Meet | MaxPreps |
```

---

## 🔄 What Changes Per Source

Only the data collection layer changes:

| Task | USA Swimming | MaxPreps |
|------|--------------|----------|
| **Get roster** | Sisense API call | Scrape roster HTML |
| **Get swimmer data** | Sisense API call | Scrape athlete page |
| **Swimmer ID** | PersonKey (int) | careerid (str) |
| **Team filter** | Team name match | School ID match |
| **Event parsing** | "50 FR SCY" | "50 Free" + infer SCY |
| **Date format** | MM/DD/YYYY | M/D/YYYY |
| **Gender** | In API response | From metadata JSON |

**But after normalization → identical!**

---

## 💡 Key Insight

**90% of the record generation logic is already source-agnostic!**

The refactoring is mostly:
1. Extract data collection into plugin interface
2. Define canonical data format
3. Implement MaxPreps plugin
4. Wire up source factory

The core business logic (finding best times, generating markdown, etc.) remains unchanged.

---

## 🎯 Benefits of Generalization

### For USA Swimming Users
- ✅ No breaking changes
- ✅ Same workflow, same commands
- ✅ Can still use existing .env configs

### For High School Users
- ✅ Can use MaxPreps as data source
- ✅ Same record generation logic
- ✅ Same markdown output format

### For Multi-Source Users
- ✅ Combine club + high school records
- ✅ Track swimmers across both systems
- ✅ Unified all-time records

### For Future Sources
- ✅ Easy to add new sources (NCAA, World Aquatics, etc.)
- ✅ Just implement `SwimDataSource` interface
- ✅ Plug-and-play architecture

---

## 📝 Example: Unified Workflow

```python
# .env configuration
DATA_SOURCE=maxpreps  # Switch sources easily
MAXPREPS_SCHOOL_SLUG=tanque-verde-hawks

# Commands work identically
$ swim-data-tool roster                    # Uses MaxPreps scraper
$ swim-data-tool import swimmers           # Scrapes athlete pages
$ swim-data-tool generate records          # Same logic, different data!

# Output: data/records/scy/records-boys.md
# Tanque Verde High School - Boys
## Team Records - Short Course Yards (SCY)

| Age Group | Time | Athlete | Age | Date | Meet | Source |
|-----------|------|---------|-----|------|------|--------|
| 15-16 | 21.45 | Wade Olsson | 15 | 9/20/2024 | CDO Classic | MaxPreps |
```

---

## 🚀 Next Steps

### Immediate (Research Phase) - ✅ Complete
1. [x] Document USA Swimming workflow
2. [x] Identify source-agnostic components
3. [x] Design abstraction layer
4. [x] Plan refactoring phases

### Short Term (Prototype)
1. [ ] Create `sources/base.py` abstract class
2. [ ] Refactor USA Swimming to plugin
3. [ ] Define canonical data format
4. [ ] Build normalizer service
5. [ ] Test with existing USA Swimming data

### Medium Term (MaxPreps Integration)
1. [ ] Implement MaxPreps source plugin
2. [ ] Test roster scraping
3. [ ] Test athlete data collection
4. [ ] Validate record generation
5. [ ] Compare outputs with USA Swimming

### Long Term (Production)
1. [ ] Multi-source support
2. [ ] Swimmer deduplication
3. [ ] Combined records
4. [ ] Documentation updates
5. [ ] Release v1.0.0

---

## 📊 Summary

### Source-Agnostic (Reusable) ✅
- ✅ Event definitions (100%)
- ✅ Age groups (100%)
- ✅ Time parsing (100%)
- ✅ Record generation logic (100%)
- ✅ Top N generation (100%)
- ✅ Markdown output (100%)
- ✅ Season filtering (100%)
- ✅ Gender filtering (100%)

### Source-Specific (Need Abstraction) 🔄
- 🔄 Data source API/scraping (0% → plugin)
- 🔄 Roster fetching (0% → plugin)
- 🔄 Swimmer data fetching (0% → plugin)
- 🔄 Team identification (50% → configurable)
- 🔄 Configuration (.env) (80% → namespaced)

### Verdict
**Approximately 85-90% of the codebase is already source-agnostic!**

The refactoring is **primarily additive** (new plugin system) rather than rewriting existing logic.

---

**Last Updated:** October 8, 2025  
**Status:** Analysis complete, ready for implementation  
**Confidence:** High - clear path forward


