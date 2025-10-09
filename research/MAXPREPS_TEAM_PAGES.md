# MaxPreps Team Stats Pages - Analysis

**Date:** October 8, 2025  
**Question:** Are team stats also embedded in metadata script tags?

---

## Answer: ❌ NO - Team Stats are HTML Only

Unlike **individual athlete pages** which have embedded JSON metadata, **team stats pages** do NOT have embedded JSON for roster or stats data. Everything is in HTML tables.

---

## Team Stats Page Structure

### URL Format
```
https://www.maxpreps.com/{state}/{city}/{school-slug}/swimming/{season}/{year}/stats/
```

**Example:**
```
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/24-25/stats/
```

### Components
- `{season}`: `fall` or `spring`
- `{year}`: Season year (e.g., `24-25` = 2024-2025)

---

## Data Format Comparison

| Page Type | Embedded JSON? | HTML Tables? | Data Source |
|-----------|----------------|--------------|-------------|
| **Individual Athlete** | ✅ YES | ✅ YES | Both |
| **Team Stats** | ❌ NO | ✅ YES | HTML only |
| **Team Roster** | ❓ Unknown | Likely YES | TBD |

---

## Extracting Roster from Team Stats Page

### HTML Structure

The team stats page has a "Best Finishes" section with tables showing the fastest athlete per event:

```html
<h2>Best Finishes</h2>
<table>
  <tr>
    <td>100 Breast</td>
    <td>
      <a href="/local/player/stats.aspx?athleteid=924b80be-ff88-4f79-b15b-b02229cea739&ssid=6046281a-ad39-4292-b0a4-12ca2e109ab8">
        Zachary Duerkop
      </a>
      00:59.51
    </td>
  </tr>
  <tr>
    <td>100 Back</td>
    <td>
      <a href="/local/player/stats.aspx?athleteid=592a52e5-0fed-4301-8c30-32e86e592ae0&ssid=6046281a-ad39-4292-b0a4-12ca2e109ab8">
        Wade Olsson
      </a>
      01:01.43
    </td>
  </tr>
</table>
```

### Athlete Link Format

```
/local/player/stats.aspx?athleteid={ATHLETE_UUID}&ssid={SEASON_UUID}
```

**Parameters:**
- `athleteid`: UUID for athlete (e.g., `592a52e5-0fed-4301-8c30-32e86e592ae0`)
- `ssid`: Season ID UUID (e.g., `6046281a-ad39-4292-b0a4-12ca2e109ab8`)

### Extraction Code

```python
from bs4 import BeautifulSoup
import re

def extract_team_roster(html):
    """Extract athlete roster from team stats page"""
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all athlete links
    athlete_links = soup.find_all('a', href=re.compile(r'/local/player/stats.aspx'))
    
    athletes = {}
    for link in athlete_links:
        href = link.get('href')
        name = link.get_text(strip=True)
        
        # Extract athleteid from URL
        match = re.search(r'athleteid=([a-f0-9-]+)', href)
        if match:
            athlete_id = match.group(1)
            
            # Deduplicate (same athlete appears in multiple events)
            if athlete_id not in athletes:
                athletes[athlete_id] = {
                    'name': name,
                    'athleteid': athlete_id,
                    'url': href
                }
    
    return list(athletes.values())
```

---

## Example Output

From Tanque Verde Hawks 2024-25:

```json
[
  {
    "name": "Jackson Eftekhar",
    "athleteid": "02780974-1c62-4520-9402-66dba1097d49",
    "url": "/local/player/stats.aspx?athleteid=02780974-1c62-4520-9402-66dba1097d49&ssid=6046281a-ad39-4292-b0a4-12ca2e109ab8"
  },
  {
    "name": "Zachary Duerkop",
    "athleteid": "924b80be-ff88-4f79-b15b-b02229cea739",
    "url": "/local/player/stats.aspx?athleteid=924b80be-ff88-4f79-b15b-b02229cea739&ssid=6046281a-ad39-4292-b0a4-12ca2e109ab8"
  },
  {
    "name": "Wade Olsson",
    "athleteid": "592a52e5-0fed-4301-8c30-32e86e592ae0",
    "url": "/local/player/stats.aspx?athleteid=592a52e5-0fed-4301-8c30-32e86e592ae0&ssid=6046281a-ad39-4292-b0a4-12ca2e109ab8"
  },
  {
    "name": "Jackson Machamer",
    "athleteid": "524be143-657c-4802-968b-8883e4d95355",
    "url": "/local/player/stats.aspx?athleteid=524be143-657c-4802-968b-8883e4d95355&ssid=6046281a-ad39-4292-b0a4-12ca2e109ab8"
  }
]
```

**Note:** Only 4 unique athletes found from "Best Finishes" table (likely only top performers shown)

---

## Team Roster Page (Better Source)

### URL Format
```
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/fall/24-25/roster/
```

This page likely has the **complete roster**, not just best performers. Should scrape this instead of team stats page for comprehensive athlete list.

---

## Workflow for School Data Collection

### Step 1: Get School Roster
```python
url = "https://www.maxpreps.com/az/tucson/{school}/swimming/fall/24-25/roster/"
html = scrape_page(url)
athletes = extract_roster(html)  # Get all athlete IDs
```

### Step 2: For Each Athlete
```python
for athlete in athletes:
    athlete_url = f"https://www.maxpreps.com{athlete['url']}"
    athlete_data = scrape_athlete_stats(athlete_url)
    # athlete_data will have embedded JSON + HTML tables
```

### Step 3: Combine Data
```python
school_data = {
    'school': 'Tanque Verde',
    'season': '2024-2025',
    'athletes': [...],  # All athlete data
    'source': 'maxpreps'
}
```

---

## Key Findings

### What Works
✅ Can extract athlete list from team stats page  
✅ Each athlete has unique UUID  
✅ Athlete links are consistent format  
✅ Deduplication by athleteid works  
✅ Roster page link is available  

### Limitations
❌ Team stats page only shows "best" performers (not complete roster)  
❌ No embedded JSON on team pages  
❌ Must scrape roster page for complete list  
❌ Duplicate athlete entries need deduplication  

### Recommendations
1. **Primary source:** Team roster page (`/roster/`)
2. **Fallback:** Team stats page (`/stats/`) for partial list
3. **For each athlete:** Individual stats page (has embedded JSON)

---

## Summary

**Team stats pages do NOT have embedded JSON metadata.**

To get a complete roster:
1. Scrape the **roster page** (not stats page)
2. Extract all athlete links
3. Visit each athlete's individual page
4. Individual pages DO have embedded JSON + HTML tables

**Files Created:**
- `scratch/maxpreps_team_athletes.json` - Extracted athlete list (4 unique)
- `scratch/maxpreps_team_page.html` - Full team stats HTML

---

**Last Updated:** October 8, 2025  
**Status:** Team page analysis complete  
**Next:** Analyze roster page structure


