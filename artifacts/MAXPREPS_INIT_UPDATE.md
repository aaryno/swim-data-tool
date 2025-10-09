# MaxPreps Init Command Update

**Date:** October 8, 2025  
**Version:** 0.10.0  
**Status:** ✅ Complete

---

## 🎉 What Changed

Updated the `swim-data-tool init` command to support **MaxPreps high school teams** without requiring USA Swimming team codes.

---

## ✨ Key Improvements

### 1. Data Source Selection ✅
When you run `swim-data-tool init`, you now choose your data source:
- **Option 1:** USA Swimming (club team)
- **Option 2:** MaxPreps (high school)

### 2. MaxPreps-Specific Questions ✅
For MaxPreps teams, you're prompted for:
- School slug (from MaxPreps URL)
- State abbreviation (e.g., az)
- City name (e.g., tucson)
- Default season (e.g., 24-25)

**NO USA Swimming team code or LSC required!** 🎊

### 3. Source-Specific Next Steps ✅
The completion message shows different workflows:

**MaxPreps workflow:**
1. Review configuration
2. Fetch roster (with season range support)
3. Import swimmers
4. Generate records
- **No "classify unattached" step** (MaxPreps has no unattached swims)

**USA Swimming workflow:**
1. Review configuration
2. Fetch roster
3. Import swimmers
4. **Classify unattached** ← Only for USA Swimming
5. Generate records

---

## 📝 Files Updated

### 1. `src/swim_data_tool/commands/init.py`
- Added data source selection prompt
- MaxPreps configuration flow (school slug, state, city, seasons)
- USA Swimming configuration flow (team code, LSC, etc.)
- Source-specific summary display
- Source-specific next steps

### 2. `templates/env.template`
- Added `DATA_SOURCE` field
- Added MaxPreps fields:
  - `MAXPREPS_SCHOOL_SLUG`
  - `MAXPREPS_STATE`
  - `MAXPREPS_CITY`
  - `MAXPREPS_SEASONS`

### 3. `tanque-verde/SETUP.md`
- Updated setup instructions to use the new init flow
- Removed manual .env creation step
- Added guidance for finding school slug from MaxPreps URL

---

## 🧪 Testing

### Try It Now!

```bash
cd ~/swimming/tanque-verde

# Run the updated init command
uv run swim-data-tool init "Tanque Verde High School"
```

### Expected Prompts:

```
Data Source:
  1. USA Swimming (club team)
  2. MaxPreps (high school)

Select data source [1]: 2

Full team name [Tanque Verde High School]: 
Team abbreviation (e.g., TFDA, TVHS): TVHS
Team nickname (optional) [TVHS]: 

MaxPreps Configuration:
Find your school at https://www.maxpreps.com
Example URL: maxpreps.com/az/tucson/tanque-verde-hawks/swimming/

School slug (from URL, e.g., 'tanque-verde-hawks'): tanque-verde-hawks
State abbreviation (e.g., az) [az]: 
City name (e.g., tucson) [tucson]: 
Default season (e.g., 24-25) [24-25]: 

Configuration Summary:

  Team: Tanque Verde High School (TVHS)
  Data Source: maxpreps
  School Slug: tanque-verde-hawks
  Location: tucson, AZ
  Default Season: 24-25
  Directory: /Users/aaryn/swimming/tanque-verde

Proceed with initialization? [Y/n]: 
```

---

## ✅ Benefits

1. **Simpler for High Schools** - No need to know USA Swimming codes
2. **Clear Workflow** - Different next steps for different sources
3. **No Manual .env Editing** - Everything configured through prompts
4. **Better User Experience** - Appropriate questions for each data source

---

## 📚 Documentation

- **Setup Guide:** `~/swimming/tanque-verde/SETUP.md`
- **Testing Guide:** `~/swimming/swim-data-tool/TESTING.md`
- **Season Range Feature:** `~/swimming/swim-data-tool/SEASON_RANGE_COMPLETE.md`

---

## 🚀 Next Steps

1. **Test Init Command** - Run init for Tanque Verde
2. **Test Season Range** - Use `--start-season` and `--end-season`
3. **Import Swimmer Data** - Test full MaxPreps workflow
4. **Generate Records** - Create all-time records (grade-based coming soon!)

---

**Ready to test!** Run the init command now! 🎉


