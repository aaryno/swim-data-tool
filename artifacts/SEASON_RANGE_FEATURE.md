# Season Range Feature

**Date:** October 8, 2025  
**Status:** ✅ Implemented and Ready for Testing

---

## 🎯 Overview

Added support for season ranges to simplify roster collection for MaxPreps (and other sources). Instead of typing multiple `--seasons` flags, you can now specify a start and end season.

---

## 🆕 New CLI Options

### Before (Cumbersome)
```bash
swim-data-tool roster --source=maxpreps \
  --seasons=12-13 \
  --seasons=13-14 \
  --seasons=14-15 \
  --seasons=15-16 \
  --seasons=16-17 \
  --seasons=17-18 \
  --seasons=18-19 \
  --seasons=19-20 \
  --seasons=20-21 \
  --seasons=21-22 \
  --seasons=22-23 \
  --seasons=23-24 \
  --seasons=24-25
```

### After (Simple)
```bash
swim-data-tool roster --source=maxpreps \
  --start-season=12-13 \
  --end-season=24-25
```

---

## 📝 Implementation Details

### Files Changed

1. **`src/swim_data_tool/commands/roster.py`**
   - Added `start_season` and `end_season` parameters to `RosterCommand.__init__()`
   - Added `_expand_season_range()` method to expand YY-YY format ranges
   - Added validation to ensure both range parameters are provided together

2. **`src/swim_data_tool/cli.py`**
   - Added `--start-season` and `--end-season` options to `roster` command
   - Updated examples to show new usage

### Season Expansion Logic

```python
def _expand_season_range(self, start: str, end: str) -> list[str]:
    """Expand season range to list of seasons.
    
    Args:
        start: Start season (e.g., "12-13")
        end: End season (e.g., "25-26")
    
    Returns:
        List of seasons (e.g., ["12-13", "13-14", ..., "25-26"])
    """
    # Parse YY-YY format
    # Handle century boundary (90s vs 2000s)
    # Generate all seasons in range
```

**Example:**
- Input: `start="12-13"`, `end="24-25"`
- Output: `["12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21", "21-22", "22-23", "23-24", "24-25"]`
- Count: 13 seasons

---

## 🧪 Testing

### Quick Test (3 seasons)
```bash
cd ~/swimming/tanque-verde-test
uv run swim-data-tool roster --source=maxpreps --start-season=22-23 --end-season=24-25
```

### Full Test (13 seasons)
```bash
cd ~/swimming/tanque-verde-test
uv run swim-data-tool roster --source=maxpreps --start-season=12-13 --end-season=24-25
```

### Verify Explicit Season Works
```bash
cd ~/swimming/tanque-verde-test
uv run swim-data-tool roster --source=maxpreps --seasons=25-26
```

### Automated Tests
```bash
cd ~/swimming/tanque-verde-test
./test_season_ranges.sh
```

See `SEASON_RANGE_TESTS.md` in tanque-verde-test for detailed testing guide.

---

## ✅ Benefits

1. **Convenience:** One command instead of 13+ flags
2. **Readability:** Clear intent (start to end)
3. **Less error-prone:** No typos in season list
4. **Flexibility:** Mix-and-match with explicit `--seasons` if needed

---

## 🔍 Validation

The implementation includes validation:
- ✅ Both `--start-season` and `--end-season` must be provided together
- ✅ Error message if only one is provided
- ✅ Works with YY-YY format (MaxPreps) and YYYY format (USA Swimming)
- ✅ Handles century boundary (99-00 transitions to 00-01)

---

## 📊 Expected Output

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
✓ Saved roster to: data/lookups/roster-maxpreps.csv
```

---

## 🚀 Next Steps

1. ✅ Test with MaxPreps (tanque-verde-test)
2. ✅ Test with USA Swimming (backwards compatibility)
3. ⏳ Test full end-to-end workflow (roster → import → records)
4. ⏳ Add grade-based record generation

---

## 📝 Related Documentation

- `TESTING.md` - Full test suite for multi-source architecture
- `tanque-verde-test/SEASON_RANGE_TESTS.md` - Quick season range tests
- `research/CLI_WORKFLOW.md` - Command-line interface patterns


