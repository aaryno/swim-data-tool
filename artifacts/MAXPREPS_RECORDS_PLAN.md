# MaxPreps Grade-Based Records Plan

**Date:** October 8, 2025  
**Version:** 0.10.0  
**Status:** Planning

---

## 🎯 Goal

Generate records for MaxPreps (high school) teams grouped by grade level, plus an "Open" category for all grades combined.

---

## 📊 Record Categories

### Grade-Based Records (Class Year)
- **Freshman** - 9th grade only
- **Sophomore** - 10th grade only
- **Junior** - 11th grade only
- **Senior** - 12th grade only

### Open Records
- **Open** - All grades combined (all-time best)

---

## 🗂️ Directory Structure

```
data/records/
├── scy/
│   ├── open/              # All grades
│   │   ├── 50-free.md
│   │   ├── 100-free.md
│   │   └── ...
│   ├── freshman/          # 9th grade
│   │   ├── 50-free.md
│   │   └── ...
│   ├── sophomore/         # 10th grade
│   │   ├── 50-free.md
│   │   └── ...
│   ├── junior/            # 11th grade
│   │   ├── 50-free.md
│   │   └── ...
│   └── senior/            # 12th grade
│       ├── 50-free.md
│       └── ...
├── lcm/
│   ├── open/
│   ├── freshman/
│   ├── sophomore/
│   ├── junior/
│   └── senior/
└── scm/
    ├── open/
    ├── freshman/
    ├── sophomore/
    ├── junior/
    └── senior/
```

---

## 🔍 Data Requirements

### Grade Information
MaxPreps roster includes:
- `grade` - Abbreviation (Fr., So., Jr., Sr.)
- `grade_numeric` - Numeric value (9, 10, 11, 12)

### Filtering Logic
```python
# Example: Sophomore records
sophomore_swims = all_swims[all_swims['grade_numeric'] == 10]

# Example: Open records (no filter)
open_swims = all_swims  # All grades
```

---

## 🚀 Implementation Plan

### 1. Update Record Generation Command
- Detect if data source is MaxPreps
- If MaxPreps, generate grade-based records
- If USA Swimming, use existing age-group logic

### 2. Grade Filtering
- Extract grade information from processed CSV files
- Filter swims by `grade_numeric` for each category
- Generate separate records for each grade level

### 3. Record File Format
Same as existing records, but with grade-level context:

```markdown
# 50 Free - Sophomore (SCY)

**Team:** Tanque Verde High School  
**Category:** Sophomore (10th Grade)  
**Course:** Short Course Yards (SCY)

## Boys

| Rank | Time | Name | Grade | Date | Meet |
|------|------|------|-------|------|------|
| 1 | 22.45 | John Doe | So. | 2024-02-15 | State Championships |
| 2 | 22.78 | ... | So. | ... | ... |

## Girls

| Rank | Time | Name | Grade | Date | Meet |
|------|------|------|-------|------|------|
| 1 | 24.12 | Jane Smith | So. | 2024-02-15 | State Championships |
```

---

## ⚙️ Configuration

### For USA Swimming
```python
# No grade-based records
# Use existing age-group logic
categories = ["all-time"]  # or age groups
```

### For MaxPreps
```python
# Grade-based records
categories = [
    "open",       # All grades
    "freshman",   # 9th grade
    "sophomore",  # 10th grade
    "junior",     # 11th grade
    "senior"      # 12th grade
]
```

---

## 📝 Key Differences from USA Swimming

| Aspect | USA Swimming | MaxPreps |
|--------|-------------|----------|
| **Grouping** | Age groups (10&U, 11-12, 13-14, etc.) | Grade levels (Fr, So, Jr, Sr) |
| **Unattached Swims** | Yes, need to classify | No unattached swims |
| **Data Source** | USA Swimming API | Web scraping |
| **Time Tracking** | By age at time of swim | By grade during season |

---

## ✅ Implementation Checklist

- [ ] Detect data source in `generate records` command
- [ ] Create grade-based directory structure
- [ ] Filter swims by `grade_numeric`
- [ ] Generate records for each grade level
- [ ] Generate "Open" records (all grades)
- [ ] Update record templates for grade context
- [ ] Test with Tanque Verde data

---

## 🧪 Testing

### Test with Tanque Verde
```bash
cd ~/swimming/tanque-verde

# Generate grade-based records
uv run swim-data-tool generate records

# Expected output:
# data/records/scy/open/
# data/records/scy/freshman/
# data/records/scy/sophomore/
# data/records/scy/junior/
# data/records/scy/senior/
```

---

## 📚 Related Files

- `src/swim_data_tool/commands/generate_records.py` - Main command
- `src/swim_data_tool/sources/maxpreps.py` - MaxPreps source
- `data/raw/swimmers/` - Raw swimmer data with grades

---

**Next:** Implement grade-based record generation!


