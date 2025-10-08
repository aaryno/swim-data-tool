# Updating the USA Swimming API Token

The USA Swimming API uses Sisense JWT tokens that expire periodically (typically every few months). When the token expires, API calls will fail and you'll need to update it.

## Quick Update Method

### 1. Get a Fresh Token from Browser

1. Open your browser and go to: https://data.usaswimming.org/datahub
2. Open Developer Tools (F12 or Cmd+Option+I)
3. Go to the **Network** tab
4. Search for a swimmer or browse data to trigger an API call
5. Look for requests to `usaswimming.sisense.com/api/datasources`
6. Click on one of these requests
7. Look at the **Request Headers**
8. Find the `authorization` header
9. Copy the Bearer token (everything after "Bearer ")

### 2. Update the Token in Code

Option A: **Edit the file directly**
```bash
# Edit src/swim_data_tool/api/usa_swimming.py
# Find the AUTH_TOKEN constant and replace with your new token
```

Option B: **Use environment variable** (future enhancement)
```bash
export USA_SWIMMING_API_TOKEN="your-token-here"
```

### 3. Commit the Change

```bash
cd ~/swimming/swim-data-tool
git add src/swim_data_tool/api/usa_swimming.py
git commit -m "fix: update USA Swimming API token (YYYY-MM-DD)"
```

## Example Token Format

The token is a JWT (JSON Web Token) that looks like:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjRhZjE4MGY5Nzg1MmIwMDJkZTU1ZDhkIiwiYXBpU2VjcmV0IjoiZjdiMjAxMDQtMDBmMC05Nzc1LTQzOWQtNGJiYjU2YWFmZTY0IiwiYWxsb3dlZFRlbmFudHMiOlsiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIl0sInRlbmFudElkIjoiNjRhYzE5ZTEwZTkxNzgwMDFiYzM5YmVhIn0.IQrXvr12kCVwL-40W_-SDGEjypdmo6PoPXVSrQAAu64
```

## When Do You Need to Update?

You'll know the token has expired when:
- `swim-data-tool init` search fails with "No swimmer found"
- `swim-data-tool roster` returns no data
- `swim-data-tool import` fails with API errors
- Commands work but return empty results

## Automated Token Refresh (Future Enhancement)

**Status:** Not yet implemented

The ideal solution would be to:
1. Visit the USA Swimming website programmatically
2. Extract the token from the page's JavaScript
3. Use the token automatically without manual updates

This requires either:
- Reverse engineering how the website generates tokens
- Using a headless browser to extract the token
- Finding an official API authentication endpoint

**Related Issue:** Token hardcoding is a known limitation

---

## Technical Details

### Token Structure

The JWT contains:
- **user**: Sisense user ID
- **apiSecret**: A UUID that changes with each token
- **allowedTenants**: Array of tenant IDs
- **tenantId**: The USA Swimming Sisense tenant

### Endpoints Using This Token

1. **Public Person Search**
   - URL: `https://usaswimming.sisense.com/api/datasources/Public%20Person%20Search/jaql`
   - Used for: Searching swimmers by name

2. **USA Swimming Times Elasticube**
   - URL: `https://usaswimming.sisense.com/api/datasources/USA%20Swimming%20Times%20Elasticube/jaql`
   - Used for: Fetching swimmer times, team rosters, meet results

### Example cURL Commands

**Search for a swimmer:**
```bash
curl 'https://usaswimming.sisense.com/api/datasources/Public%20Person%20Search/jaql' \
  -H 'authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'content-type: application/json' \
  --data-raw '{
    "metadata": [
      {"jaql": {"title": "Name", "dim": "[Persons.FullName]", "datatype": "text"}},
      {"jaql": {"title": "PersonKey", "dim": "[Persons.PersonKey]", "datatype": "numeric"}},
      {"jaql": {"title": "FirstAndPreferredName", "dim": "[Persons.FirstAndPreferredName]", "datatype": "text", "filter": {"contains": "John"}}, "panel": "scope"},
      {"jaql": {"title": "LastName", "dim": "[Persons.LastName]", "datatype": "text", "filter": {"contains": "Smith"}}, "panel": "scope"}
    ],
    "datasource": "Public Person Search",
    "count": 50
  }'
```

---

**Last Updated:** 2025-10-08


