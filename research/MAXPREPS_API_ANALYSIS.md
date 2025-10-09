# MaxPreps API Analysis - High School Swimming Data

**Date:** October 8, 2025  
**Finding:** ⚠️ **No JSON API - Server-Side Rendered HTML Only**

---

## 🔍 Key Discovery

MaxPreps does **NOT** expose a JSON API for athlete data. All data is **server-side rendered** directly into the HTML page. You must scrape the HTML to extract athlete statistics.

---

## 📍 URL Structure

### Athlete Stats Page

```
https://www.maxpreps.com/{state}/{city}/{school-slug}/athletes/{athlete-slug}/{sport}/stats/
```

**Example:**
```
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/athletes/wade-olsson/swimming/stats/
```

### Path Parameters

| Parameter | Example | Description |
|-----------|---------|-------------|
| `{state}` | `az` | Two-letter state code (lowercase) |
| `{city}` | `tucson` | City name (lowercase, no spaces) |
| `{school-slug}` | `tanque-verde-hawks` | School name slug (lowercase, hyphens) |
| `athlete-slug` | `wade-olsson` | Athlete name slug (lowercase, hyphens) |
| `{sport}` | `swimming` | Sport name (lowercase) |

### Query Parameters

```
?careerid={SHORT_ID}&sportSeasonId={SEASON_UUID}
```

| Parameter | Example | Description | Required |
|-----------|---------|-------------|----------|
| `careerid` | `10aavdb9t0tee` | Short alphanumeric ID (12-13 chars) | Yes |
| `sportSeasonId` | `6046281a-ad39-4292-b0a4-12ca2e109ab8` | UUID for season | Yes |

**Full URL Example:**
```
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/athletes/wade-olsson/swimming/stats/?careerid=10aavdb9t0tee&sportSeasonId=6046281a-ad39-4292-b0a4-12ca2e109ab8
```

---

## 📦 Response Format

### HTTP Response
- **Content-Type:** `text/html; charset=utf-8`
- **Status:** 200 OK
- **Format:** Server-side rendered HTML

### No API Endpoints Found

After analyzing network traffic, **NO athlete data APIs** were discovered. All XHR/Fetch calls are for:
- Advertisements (Google, Amazon, Criteo)
- Analytics (Adobe, Paramount)
- Cookie consent (OneTrust)
- Configuration

---

## 📊 Data Structure in HTML

### 1. Athlete Metadata (Embedded JSON)

**Location:** `<script>` tag #17 (approximately)

**Pattern:** Search for script containing `"careerName"`

**Structure:**
```json
{
  "pageError": 0,
  "pageNum": 0,
  "careerId": "6d9f59f2-c7f1-420a-b47a-4194c59dbd49",
  "careerName": "Wade Olsson",
  "siteHier": ["boys", "swimming"],
  "siteSection": "boys",
  "siteType": "desktop web",
  "pageOntologyId": "35563",
  "pageType": "players",
  "pageName": "/local/career/gendersport/stats.aspx",
  "pageTypeId": "6866",
  "schoolId": "c2e9a48b-11a5-4795-a593-3a96b187dd3d",
  "schoolName": "Tanque Verde (Tucson, AZ)",
  "state": "AZ",
  "gender": "Boys",
  "sportName": "Swimming",
  "teamLevel": "Varsity",
  "season": "Fall",
  "year": "25-26",
  "ssid": "89e1c179-5dad-445f-aca0-1206b64f92e3",
  "content": "career,career-current-grade-11,career-manually-managed,...",
  "siteRsid": "cbsimaxprepssite",
  "brandPlatformId": "maxpreps_site_desktop",
  "isAvia": false,
  "contentFramework": "Desktop"
}
```

**Key Fields:**
- `careerId`: Full UUID (differs from query param `careerid`)
- `careerName`: Athlete full name
- `schoolId`: UUID for school
- `schoolName`: School name with city/state
- `state`: Two-letter state code
- `gender`: "Boys" or "Girls"
- `sportName`: "Swimming"
- `year`: Season year (e.g., "25-26" = 2025-2026)
- `ssid`: Sport season ID (matches query param `sportSeasonId`)

---

### 2. Best Finishes Table

**Location:** HTML section with `<h2 id="best_finishes_{uuid}">Best Finishes</h2>`

**HTML Structure:**
```html
<h2 id="best_finishes_e29634a8-6eea-44fc-b033-7f9abf82fc79">Best Finishes</h2>
<div class="cf">
  <div class="column1">
    <table class="mx-grid">
      <thead>
        <tr>
          <th class="first">Event</th>
          <th class="last">Result</th>
        </tr>
      </thead>
      <tbody>
        <tr class="first">
          <td class="first">
            100 Breast
            <a href="#category_e29634a8-6eea-44fc-b033-7f9abf82fc79_100_breast">View Times</a>
          </td>
          <td class="last">
            <span>01:00.35</span>
          </td>
        </tr>
        <tr class="alternate">
          <td class="first">
            200 Individual Medley
            <a href="#category_e29634a8-6eea-44fc-b033-7f9abf82fc79_200_individual_medley">View Times</a>
          </td>
          <td class="last">
            <span>02:00.20</span>
          </td>
        </tr>
        <tr class="last">
          <td class="first">
            200 Free Relay
            <a href="#category_e29634a8-6eea-44fc-b033-7f9abf82fc79_200_free_relay">View Times</a>
          </td>
          <td class="last">
            <span>01:31.81</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

**Data to Extract:**
- Event name (e.g., "100 Breast", "200 Individual Medley")
- Best time (e.g., "01:00.35")
- Anchor link to detailed results

---

### 3. Meet-by-Meet Statistics

**Location:** Multiple sections with `id="category_{uuid}_{event_slug}"`

**HTML Structure:**
```html
<div id="category_e29634a8-6eea-44fc-b033-7f9abf82fc79_100_breast">
  <h4>100 Breast</h4>
  <table>
    <thead>
      <tr>
        <th>Date</th>
        <th>Opponent</th>
        <th>Round</th>
        <th>Splits</th>
        <th>Time</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>9/20/2025</td>
        <td>
          <a href="/local/stats/contest.aspx?ssid=89e1c179-5dad-445f-aca0-1206b64f92e3&contestid=a2db1b29-526b-41dc-8fc0-abb63036a3b6&eventtype=medleyrelay200&round=preliminary">
            Canyon del Oro Classic (Tucson, AZ)
          </a>
        </td>
        <td>Final</td>
        <td>01:00.35</td>
        <td></td>
      </tr>
      <tr>
        <td>9/27/2025</td>
        <td>
          <a href="/local/stats/contest.aspx?ssid=89e1c179-5dad-445f-aca0-1206b64f92e3&contestid=44352254-778d-4db2-80ed-2cffc33d3417&eventtype=medleyrelay200&round=preliminary">
            Arena High School Classic (Tucson, AZ)
          </a>
        </td>
        <td>Final</td>
        <td>01:00.49</td>
        <td></td>
      </tr>
    </tbody>
  </table>
</div>
```

**Data to Extract:**
- Date (MM/DD/YYYY format)
- Meet name and location
- Meet URL (for additional details)
- Round (Prelims/Finals/etc.)
- Splits (if available)
- Time (MM:SS.SS format)

**Meet URL Parameters:**
- `ssid`: Sport season ID
- `contestid`: UUID for specific meet
- `eventtype`: Event type code
- `round`: preliminary/finals

---

## 🛠️ Extraction Strategy

### Recommended Approach: Playwright + BeautifulSoup

```python
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

def scrape_maxpreps_athlete(url):
    """
    Scrape athlete stats from MaxPreps
    
    Args:
        url: Full MaxPreps athlete stats URL
    
    Returns:
        dict with metadata, best_times, and meet_results
    """
    
    # Load page with Playwright (handles JavaScript)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)  # Wait for any dynamic content
        html = page.content()
        browser.close()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Extract metadata from script tag
    metadata = None
    for script in soup.find_all('script'):
        if script.string and 'careerName' in script.string:
            match = re.search(r'\{[^<>]*"careerName"[^<>]*\}', script.string)
            if match:
                try:
                    metadata = json.loads(match.group(0))
                    break
                except json.JSONDecodeError:
                    pass
    
    # 2. Extract best times
    best_times = []
    best_finishes = soup.find('h2', id=re.compile(r'best_finishes_'))
    if best_finishes:
        table = best_finishes.find_next('table', class_='mx-grid')
        if table:
            for row in table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    event = cols[0].get_text(strip=True)
                    # Remove "View Times" link text
                    event = re.sub(r'View Times$', '', event).strip()
                    time = cols[1].get_text(strip=True)
                    best_times.append({
                        'event': event,
                        'best_time': time
                    })
    
    # 3. Extract meet-by-meet results
    meet_results = {}
    for div in soup.find_all('div', id=re.compile(r'category_[a-f0-9-]+_\w+')):
        event_id = div.get('id')
        event_name = div.find('h4').get_text(strip=True) if div.find('h4') else None
        
        meets = []
        table = div.find('table')
        if table and table.find('tbody'):
            for row in table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 5:
                    date = cols[0].get_text(strip=True)
                    meet_link = cols[1].find('a')
                    meet_name = meet_link.get_text(strip=True) if meet_link else ''
                    meet_url = meet_link.get('href') if meet_link else ''
                    round_type = cols[2].get_text(strip=True)
                    splits = cols[3].get_text(strip=True)
                    time = cols[4].get_text(strip=True)
                    
                    meets.append({
                        'date': date,
                        'meet_name': meet_name,
                        'meet_url': meet_url,
                        'round': round_type,
                        'splits': splits,
                        'time': time
                    })
        
        if event_name:
            meet_results[event_name] = meets
    
    return {
        'metadata': metadata,
        'best_times': best_times,
        'meet_results': meet_results
    }
```

---

## 📝 Data Model

### Canonical Swim Format

```python
{
    "swimmer_id": "wade-olsson-10aavdb9t0tee",  # From URL
    "swimmer_name": "Wade Olsson",              # From metadata
    "school_id": "c2e9a48b-11a5-4795-a593-3a96b187dd3d",
    "school_name": "Tanque Verde",
    "city": "Tucson",
    "state": "AZ",
    "gender": "Boys",
    "grade": "11",                              # From metadata.content
    "season": "2025-2026",                      # From metadata.year
    
    "swims": [
        {
            "event": "100 Breast",
            "event_code": "100-breast-scy",     # Normalize
            "time": "01:00.35",
            "time_seconds": 60.35,              # Convert
            "date": "2025-09-20",               # Parse
            "meet_name": "Canyon del Oro Classic",
            "meet_location": "Tucson, AZ",
            "round": "Final",
            "source": "maxpreps",
            "source_url": "https://www.maxpreps.com/..."
        }
    ]
}
```

---

## 🚀 Implementation Plan

### Phase 1: Single Athlete Scraper (1 day)
- [x] Analyze HTML structure
- [ ] Build scraper for one athlete
- [ ] Extract all swim times
- [ ] Test with multiple athletes

### Phase 2: School Roster Discovery (2-3 days)
- [ ] Find school roster pages
- [ ] Extract all athlete URLs from roster
- [ ] Handle pagination if needed
- [ ] Build school → athletes mapping

### Phase 3: MaxPreps Source Plugin (1 week)
- [ ] Implement `MaxPrepsSource` class
- [ ] Rate limiting / polite scraping
- [ ] Caching layer
- [ ] Error handling for missing data

### Phase 4: Integration (1 week)
- [ ] Add to multi-source architecture
- [ ] Combine with USA Swimming data
- [ ] Handle duplicate detection
- [ ] Generate unified records

---

## ⚖️ Legal Considerations

### Terms of Service
- Review MaxPreps ToS before scraping
- Implement rate limiting (1-2 requests/second max)
- Respect robots.txt
- Add User-Agent header
- Cache results to minimize requests

### Best Practices
```python
headers = {
    'User-Agent': 'swim-data-tool/0.9.0 (Educational/Research)',
    'Accept': 'text/html',
}

# Rate limiting
import time
time.sleep(1)  # 1 second between requests
```

---

## 🎯 Advantages vs AIA PDFs

| Aspect | MaxPreps | AIA PDFs |
|--------|----------|----------|
| **Data Source** | All meets | State championships only |
| **Format** | Clean HTML | Unstructured PDFs |
| **Parsing** | BeautifulSoup | Complex regex |
| **Coverage** | Complete season | Top qualifiers only |
| **Updates** | Real-time | Annual |
| **Individual Pages** | Yes | No |
| **Relay Names** | Included | Names only |
| **Grade Level** | Yes | Yes |
| **Unique IDs** | Yes (careerid) | No |

**Verdict:** ⭐⭐⭐⭐⭐ **MaxPreps is FAR superior to AIA PDFs for high school swimming data**

---

## 🔗 Related URLs

### School Pages
```
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/roster/
```

### Team Stats
```
https://www.maxpreps.com/az/tucson/tanque-verde-hawks/swimming/stats/
```

### Meet Results
```
https://www.maxpreps.com/local/stats/contest.aspx?ssid={SSID}&contestid={CONTEST_ID}
```

---

## 📊 Summary

### What We Know
✅ URL structure is predictable  
✅ Data is server-side rendered in HTML  
✅ Metadata available as embedded JSON  
✅ Stats in clean HTML tables  
✅ Meet-by-meet progression available  
✅ Unique athlete IDs (careerid)  
✅ School roster pages exist  

### What We Don't Know
❓ How to discover all athlete URLs systematically  
❓ Rate limiting thresholds  
❓ Data retention (how far back?)  
❓ Coverage (all AZ schools or partial?)  
❓ Update frequency  

### Next Steps
1. Test scraper with 10-20 athletes
2. Find school roster discovery method
3. Implement rate-limited batch scraper
4. Build MaxPreps source plugin

---

**Last Updated:** October 8, 2025  
**Status:** Analysis complete, ready for implementation  
**Recommendation:** Use MaxPreps as PRIMARY source for AZ high school swimming (abandon AIA PDF parsing)


