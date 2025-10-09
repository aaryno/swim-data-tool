# Arizona Interscholastic Association (AIA) Swimming - Data Source Research

**Date:** October 8, 2025  
**Purpose:** Research AIA high school swimming data for potential swim-data-tool integration

---

## Overview

The Arizona Interscholastic Association (AIA) governs high school athletics in Arizona, including swimming and diving. Unlike USA Swimming's centralized API, AIA data is published primarily as PDF documents.

**Website:** [https://aiaonline.org](https://aiaonline.org)

---

## Available Data Sources

### 1. State Championship Results (2001-2024)

AIA publishes state championship results as PDF documents. Available years:

| Year | File ID | Title | URL |
|------|---------|-------|-----|
| 2024 | 18411 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/18411/2024-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2023 | 18187 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/18187/2023-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2022 | 17935 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/17935/2022-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2021 | 17672 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/17672/2021-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2020 | 17252 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/17252/2020-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2019 | 16845 | Divisions I-III State Championships & Meet of Champions | [PDF](https://aiaonline.org/files/16845/2019-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2018 | 16553 | Divisions I-III State Championships & Meet of Champions | [PDF](https://aiaonline.org/files/16553/2018-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2017 | 16054 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/16054/2017-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2016 | 15661 | Swimming and Diving Divisions I-III State Championships | [PDF](https://aiaonline.org/files/15661/2016-swimming-and-diving-divisions-i-iii-state-championships.pdf) |
| 2015 | 15247 | Swimming and Diving Divisions I-II State Championships | [PDF](https://aiaonline.org/files/15247/2015-swimming-and-diving-divisions-i-ii-state-championships.pdf) |
| 2014 | 14651 | Swimming and Diving Divisions I-II State Championships | [PDF](https://aiaonline.org/files/14651/2014-swimming-and-diving-divisions-i-ii-state-championships.pdf) |
| 2013 | 14249 | Swimming and Diving Divisions I-II State Championships | [PDF](https://aiaonline.org/files/14249/2013-swimming-and-diving-divisions-i-ii-state-championships.pdf) |
| 2012 | 13462 | Swimming and Diving Divisions I-II State Championships | [PDF](https://aiaonline.org/files/13462/2012-swimming-and-diving-divisions-i-ii-state-championships.pdf) |
| 2011 | 12611 | Swimming and Diving Divisions I-II State Championships | [PDF](https://aiaonline.org/files/12611/2011-swimming-and-diving-divisions-i-ii-state-championships.pdf) |
| 2010 | 11757 | Swimming and Diving Divisions I-II State Championships | [PDF](https://aiaonline.org/files/11757/2010-swimming-and-diving-divisions-i-ii-state-championships.pdf) |
| 2009 | 10504 | Swimming and Diving 1A-5A State Championships | [PDF](https://aiaonline.org/files/10504/2009-swimming-and-diving-1a-5a-state-championships.pdf) |
| 2008 | 9361 | Swimming and Diving 1A-5A State Championships | [PDF](https://aiaonline.org/files/9361/2008-swimming-and-diving-1a-5a-state-championships.pdf) |
| 2007 | 7844 | Swimming and Diving 1A-5A State Championships | [PDF](https://aiaonline.org/files/7844/2007-swimming-and-diving-1a-5a-state-championships.pdf) |
| 2006 | 6039 | Swimming and Diving 4A-5A State Championships | [PDF](https://aiaonline.org/files/6039/2006-swimming-and-diving-4a-5a-state-championships.pdf) |
| 2005 | 4023 | Swimming and Diving 4A-5A State Championships | [PDF](https://aiaonline.org/files/4023/2005-swimming-and-diving-4a-5a-state-championships.pdf) |
| 2004 | 722 | Swimming and Diving 4A-5A State Championships | [PDF](https://aiaonline.org/files/722/2004-swimming-and-diving-4a-5a-state-championships.pdf) |
| 2003 | 3826 | Swimming and Diving 5A State Championships | [PDF](https://aiaonline.org/files/3826/2003-swimming-and-diving-5a-state-championships.pdf) |
| 2002 | 7268 | Swimming and Diving 5A State Championships | [PDF](https://aiaonline.org/files/7268/2002-swimming-and-diving-5a-state-championships.pdf) |
| 2001 | 7171 | Swimming and Diving 4A-5A State Championships | [PDF](https://aiaonline.org/files/7171/2001-swimming-and-diving-4a-5a-state-championships.pdf) |

**Coverage:** 24 years (2001-2024)

### 2. Division Structure Evolution

AIA swimming divisions have changed over time:

- **2001-2006:** 4A-5A only (larger schools)
- **2007-2009:** 1A-5A (all schools)
- **2010-2015:** Divisions I-II (two divisions)
- **2016-2024:** Divisions I-III (three divisions, current structure)

**Note:** "Meet of Champions" added in 2018-2019 (top performers across divisions)

---

## Data Characteristics

### Format
- **Primary Format:** PDF documents
- **Challenge:** Not machine-readable without PDF parsing
- **Structure:** Likely results tables with swimmer names, schools, times, places

### Content (Expected)
Based on typical high school state championship programs:

1. **Individual Events**
   - 200 Medley Relay
   - 200 Free
   - 200 IM
   - 50 Free
   - 100 Fly
   - 100 Free
   - 500 Free
   - 200 Free Relay
   - 100 Back
   - 100 Breast
   - 400 Free Relay

2. **Data Fields (Expected)**
   - Swimmer name
   - School name
   - Grade level (Fr, So, Jr, Sr)
   - Seed time
   - Finals time
   - Place (1st-16th typically)
   - Division (I, II, or III)

3. **Team Scoring**
   - Team points
   - Team standings
   - Individual and relay contributions

### Course
- **SCY (Short Course Yards)** - All Arizona high school swimming
- Season: November - February
- State Championships: Typically February

---

## Challenges

### 1. Data Accessibility
- ❌ **No Public API** - Unlike USA Swimming's Sisense API
- ❌ **PDF Format** - Requires parsing (PyPDF2, pdfplumber, or Tabula)
- ❌ **Inconsistent Formatting** - PDF layout may change year to year
- ⚠️ **State Championships Only** - No dual meets, invitationals, or section results

### 2. Data Completeness
- **Limited to qualifiers** - Only swimmers who qualified for state
- **Missing regular season** - No comprehensive season data
- **No unique IDs** - Students identified by name + school + year only
- **Graduation data** - Students leave system after 4 years max

### 3. Privacy Considerations
- **FERPA compliance** - High school students have different privacy protections
- **Parental consent** - May be required for public display
- **Age restrictions** - Most swimmers are minors (14-18 years old)

### 4. Data Gaps
- **No section meets** - Section championships not published centrally
- **No invitational results** - Large invitationals not documented
- **No dual meet data** - Regular season meets unavailable
- **Limited historical depth** - Only state championships available

---

## Alternative Data Sources

### 1. Athletic.net
**URL:** [https://www.athletic.net](https://www.athletic.net)

- **Coverage:** High school swimming results across many states
- **Format:** HTML results pages (scrapable)
- **Content:** Individual meets, season bests, rankings
- **Advantages:**
  - More comprehensive than state championships only
  - Structured HTML (easier to parse than PDFs)
  - Includes regular season meets
  - Provides season rankings

**Challenges:**
- Requires web scraping
- May have terms of service restrictions
- Coverage depends on schools/meets voluntarily uploading results

### 2. Direct School Athletic Sites
- Some schools publish meet results on athletic department websites
- Inconsistent format and availability
- Time-consuming to aggregate

### 3. Meet Mobile / Hy-Tek Results
- Some Arizona meets use Hy-Tek Meet Manager
- Results sometimes posted to MeetMobile.us
- Inconsistent availability

---

## Implementation Strategy

### Phase 1: PDF Parser for State Championships

**Scope:** Extract results from 2001-2024 state championship PDFs

**Tools:**
```python
# PDF parsing options
import pdfplumber  # Best for tables
import PyPDF2      # Basic text extraction
import tabula      # Convert PDF tables to DataFrames
```

**Workflow:**
1. Download all 24 PDF files
2. Analyze PDF structure (manual inspection)
3. Build parser for most common format
4. Handle format variations by year
5. Extract to canonical DataFrame format
6. Store in local database

**Expected Output:**
```python
{
    "swimmer_name": "John Smith",
    "school": "Desert Vista High School",
    "grade": "Jr",
    "division": "I",
    "event": "50 Free",
    "prelim_time": "21.45",
    "finals_time": "21.12",
    "place": 3,
    "year": 2024,
    "meet": "AIA State Championships",
    "course": "SCY"
}
```

### Phase 2: Athletic.net Integration

**Scope:** Scrape more comprehensive season data

**Workflow:**
1. Research Athletic.net structure for Arizona
2. Build school/swimmer search
3. Extract season results
4. Aggregate by school/swimmer
5. Merge with state championship data

### Phase 3: Unified High School Source

**Implementation:**
```python
# src/swim_data_tool/sources/aia_arizona.py

class AIAArizonaSource(SwimDataSource):
    """
    Arizona high school swimming data source
    
    Data Sources:
    1. AIA State Championships (2001-2024) - PDF parsing
    2. Athletic.net - Web scraping (optional)
    """
    
    def __init__(self):
        self.pdf_cache = "data/cache/aia_pdfs/"
        self.state_results_db = "data/cache/aia_state_results.db"
    
    def get_team_roster(self, school_name: str, seasons: List[str]) -> pd.DataFrame:
        """
        Build roster from state championship appearances
        
        Note: Limited to swimmers who qualified for state
        """
        swimmers = []
        for season in seasons:
            year = int(season)
            state_results = self._get_state_results(year)
            school_swimmers = state_results[
                state_results['school'] == school_name
            ]['swimmer_name'].unique()
            swimmers.extend(school_swimmers)
        
        return pd.DataFrame({
            'name': list(set(swimmers)),
            'school': school_name,
            'source': 'aia_state_championships'
        })
    
    def _get_state_results(self, year: int) -> pd.DataFrame:
        """Extract results from state championship PDF"""
        pdf_file = self._download_pdf(year)
        results = self._parse_state_championship_pdf(pdf_file)
        return results
    
    def _parse_state_championship_pdf(self, pdf_path: str) -> pd.DataFrame:
        """Parse state championship PDF to DataFrame"""
        # Implementation using pdfplumber or tabula
        pass
```

---

## Use Cases

### 1. High School Team Records
A high school coach wants to track team records:
```bash
swim-data-tool init "Desert Vista Thunder" --source=aia_arizona
swim-data-tool roster --seasons=2020 --seasons=2021 --seasons=2022
swim-data-tool generate records
```

### 2. Club Swimmer with High School Times
A club swimmer also competes for high school:
```bash
# Import from both sources
swim-data-tool import swimmer "John Smith" --source=usa_swimming
swim-data-tool import swimmer "John Smith" --source=aia_arizona

# Classify high school swims separately
swim-data-tool classify unattached --high-school=separate

# Generate combined records
swim-data-tool generate records --source=all
```

### 3. State Championship Analysis
Analyze trends across Arizona high school swimming:
```bash
swim-data-tool analyze-state-meet --division=I --years=2015-2024
```

---

## Data Model Mapping

### AIA → Canonical Format

| AIA Field | Canonical Field | Notes |
|-----------|----------------|-------|
| Swimmer Name | `swimmer_id` | Use name+school+year (no unique ID) |
| School Name | `team_name` | Full school name |
| Grade Level | `metadata.grade` | Fr/So/Jr/Sr |
| Division | `metadata.division` | I, II, or III |
| Event | `event_code` | Normalize to "50-free-scy" |
| Finals Time | `time_seconds` | Convert MM:SS.SS to seconds |
| Place | `metadata.place` | 1-16+ |
| Meet | `meet_name` | "AIA State Championships 2024" |

### Student Identifier Strategy

Since AIA has no unique student ID:
```python
student_id = f"{school_code}_{normalize_name(name)}_{grad_year}"
# Example: "DV_john_smith_2025"
```

**Collision handling:**
- Add middle initial if available
- Use birthdate if available (unlikely in public data)
- Manual disambiguation for edge cases

---

## Privacy & Legal Considerations

### FERPA (Family Educational Rights and Privacy Act)
- ✅ **Athletic results are generally public** - Meet results published publicly
- ✅ **Names in context of sports are OK** - Similar to yearbooks
- ⚠️ **No educational records** - Don't include grades, test scores, etc.
- ⚠️ **No identifying info** - Don't include addresses, phone numbers

### Best Practices
1. **Public data only** - Only use publicly published meet results
2. **No PII** - Don't collect birthdates, student IDs, contact info
3. **Opt-out mechanism** - Allow parents/students to request removal
4. **Historical only** - Consider aging off data after graduation + X years
5. **Team-level aggregation** - Focus on team records, not individual tracking

### Terms of Service
- **AIA PDFs:** Publicly available documents (likely OK to parse)
- **Athletic.net:** Review ToS before scraping
- **Meet Mobile:** Review ToS before scraping

---

## Proof of Concept Tasks

### Task 1: PDF Parser Prototype
**Goal:** Successfully parse 2024 state championship results

**Steps:**
1. Download 2024 PDF manually
2. Inspect structure with PDF viewer
3. Try pdfplumber, PyPDF2, and tabula
4. Extract one event (e.g., 50 Free Division I)
5. Convert to structured DataFrame
6. Validate accuracy against PDF

**Success Criteria:**
- Extract swimmer names (>90% accuracy)
- Extract schools (>95% accuracy)  
- Extract times (>99% accuracy)
- Extract places correctly

### Task 2: Historical Coverage Test
**Goal:** Parse multiple years to test format consistency

**Steps:**
1. Parse 2024, 2020, 2015, 2010, 2005
2. Document format differences
3. Build flexible parser with format detection
4. Create error handling for edge cases

### Task 3: Sample School Records
**Goal:** Generate records for one high school

**Steps:**
1. Choose test school (e.g., Desert Vista)
2. Extract all Desert Vista times 2001-2024
3. Generate school records by event
4. Compare to official school records (if available)
5. Validate accuracy

---

## Timeline Estimate

### Minimal Viable Product (MVP)
- **2-3 weeks:** PDF parser + state championship database
- **1 week:** AIA source plugin architecture
- **1 week:** Testing and validation
- **Total:** ~1 month for state championship support

### Full Implementation
- **MVP:** 1 month (above)
- **Athletic.net integration:** 2-3 weeks
- **Multi-source support:** 1-2 weeks
- **Privacy/opt-out system:** 1 week
- **Total:** 2-3 months for comprehensive high school support

---

## Next Steps

### Immediate (This Session)
1. ✅ Document AIA data sources
2. ✅ Download sample PDFs (2024, 2020, 2015)
3. ✅ Analyze PDF structure
4. ⏳ Prototype parser for one PDF

**PDF Analysis Results:**
- **Format:** HY-TEK's Meet Manager (v6.0-7.0)
- **Structure:** Text-based layout (NOT table-structured)
- **Pages:** 31-59 pages per championship
- **Consistency:** Similar format across years
- **Challenge:** No structured tables - requires regex-based text parsing
- **Content:** Swimmer names, schools, times, places embedded in text flow

### Short Term (Next Session)
1. Build PDF parser for state championships
2. Create AIA data cache
3. Test with multiple years
4. Extract sample school data

### Medium Term (Next Sprint)
1. Design source abstraction layer
2. Refactor USA Swimming to plugin
3. Implement AIA plugin
4. Test with real high school

---

## Resources

### Documentation
- **AIA Website:** https://aiaonline.org
- **Athletic.net:** https://www.athletic.net
- **FERPA Guidelines:** https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html

### Python Libraries
```bash
# PDF parsing
pip install pdfplumber        # Best for tables
pip install PyPDF2            # Text extraction
pip install tabula-py         # PDF tables to DataFrames

# Web scraping
pip install beautifulsoup4    # HTML parsing
pip install selenium          # JavaScript-heavy sites
pip install requests-html     # Async scraping
```

### Similar Projects
- **Milesplit** - Track & field results (similar model)
- **MaxPreps** - High school sports stats
- **DyeStatCal** - California cross country (volunteer-maintained)

---

## Decision Points

### Question 1: Scope of MVP
**Option A:** State championships only (easier, limited data)  
**Option B:** Include Athletic.net (harder, more complete)

**Recommendation:** Start with Option A, add Option B later

### Question 2: Historical Depth
**How many years to parse initially?**
- Minimum: 2020-2024 (5 years, recent)
- Recommended: 2015-2024 (10 years, good coverage)
- Maximum: 2001-2024 (24 years, complete history)

**Recommendation:** Start with 2015-2024, backfill to 2001 later

### Question 3: Privacy Approach
**How to handle student privacy?**
- Option A: No special handling (public data)
- Option B: Age off data after 5 years
- Option C: Opt-out system

**Recommendation:** Option A with C (opt-out available on request)

---

## Conclusion

AIA high school swimming data is **feasible but challenging** to integrate:

**✅ Pros:**
- 24 years of state championship data available
- Publicly accessible PDFs
- Clear use case for high school teams
- Complements USA Swimming club data

**❌ Cons:**
- PDF parsing required (not as clean as API)
- State championships only (incomplete season data)
- No unique student identifiers
- Privacy considerations for minors
- Format inconsistencies across years

**Verdict:** Worth implementing as optional source, starting with state championships as MVP, potentially expanding to Athletic.net for more complete data.

---

**Last Updated:** October 8, 2025  
**Status:** Research phase - Ready for prototype implementation  
**Next Action:** Download and analyze sample PDFs

