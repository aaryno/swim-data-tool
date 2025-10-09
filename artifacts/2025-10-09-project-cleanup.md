# Project Structure Cleanup

**Date:** 2025-10-09  
**Status:** ✅ Complete

---

## Summary

Cleaned up swim-data-tool repository structure according to project guidelines:
- Moved test/debug scripts to `scratch/`
- Moved Claude summaries to `artifacts/`
- Moved workflow docs to `research/`
- Updated `claude.md` documentation

---

## Files Moved

### From `/Users/aaryn/swimming/` root → `swim-data-tool/scratch/`
- `check_env.py` - Environment checking script
- `create_swas_env.py` - SWAS setup script
- `run_top10_uv.sh` - Shell script for top10
- `test_basic.py` - Basic testing script
- `test_import.py` - Import testing script

### From `swim-data-tool/` root → `scratch/`
- `run_top10_logged.py` - Logged top10 execution
- `test_top10_swas.py` - SWAS top10 testing

### From `swim-data-tool/` root → `artifacts/`
- `IMPLEMENTATION_COMPLETE.md` - Multi-source implementation summary
- `MAXPREPS_INIT_UPDATE.md` - MaxPreps initialization notes
- `MAXPREPS_RECORDS_PLAN.md` - MaxPreps records planning
- `SEASON_RANGE_COMPLETE.md` - Season range feature completion
- `SEASON_RANGE_FEATURE.md` - Season range feature docs
- `RELEASE_NOTES_0.11.0.md` - Release notes
- `TESTING.md` - Multi-source testing guide

### From `swim-data-tool/` root → `research/`
- `MAXPREPS_WORKFLOW.md` - MaxPreps workflow guide

---

## Current Structure

### ✅ Clean Root Directory
Only essential files in `swim-data-tool/` root:
- `README.md` - User documentation
- `CHANGELOG.md` - Version history
- `LICENSE` - MIT license
- `claude.md` - AI development context
- `VERSION` - Version number
- `pyproject.toml` - Package configuration
- `uv.lock` - Dependency lock file

### ✅ Organized Directories

**`artifacts/`** - AI-generated documentation
- Session summaries (session-*.md)
- Release summaries (v*.md)
- Implementation notes (*_COMPLETE.md)
- Feature docs (*_FEATURE.md)
- Testing guides (TESTING.md)

**`research/`** - Technical analysis and planning
- API analysis docs
- Workflow guides
- Architecture planning
- Session notes

**`scratch/`** - Test and debug scripts (gitignored)
- Test scripts (test_*.py)
- Debug scripts (debug_*.py)
- Check scripts (check_*.py)
- One-off runners (run_*.py, *.sh)
- Setup scripts (create_*.py)

**`src/`** - Production code
- Main package code
- API clients
- Commands
- Models
- Services

**`tests/`** - Unit tests
- Test suites by module
- Pytest configuration

**`templates/`** - Init templates
- Environment templates
- README templates
- Configuration templates

**`docs/`** - User documentation
- Usage guides
- API token updates

---

## Version File Clarification

### Two Different Version Files

1. **`VERSION` in tool repo** (`swim-data-tool/VERSION`)
   - Source of truth for tool version
   - Updated on every release
   - Read by `version.py` at runtime
   - Example: `0.9.0`

2. **`.swim-data-tool-version` in team repos** (NOT in tool repo)
   - Created by `swim-data-tool init` command
   - Records which tool version initialized the team
   - Helps track compatibility
   - Example: `0.9.0`

### Not Redundant!
- `VERSION` = "What version is the tool?"
- `.swim-data-tool-version` = "What version initialized this team?"

---

## Benefits

1. **Clear root directory** - Easy to navigate, no clutter
2. **Organized artifacts** - All Claude summaries in one place
3. **Proper scratch usage** - All test scripts isolated
4. **Better separation** - Research vs artifacts vs production code
5. **Updated docs** - claude.md reflects new organization

---

## Guidelines for Future

### ✅ DO
- Put test/debug scripts in `scratch/`
- Put AI summaries in `artifacts/`
- Put technical analysis in `research/`
- Keep root directory minimal

### ❌ DON'T
- Create .py files in project root
- Create .md files in root (except README, CHANGELOG, claude.md)
- Commit scratch/ contents
- Mix production code with test scripts

---

**Result:** Clean, organized, maintainable project structure! 🎉

