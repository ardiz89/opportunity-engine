# Project Constitution

## 1. Vision
**North Star:** Automatically generate a multi-tab Excel report for Year 2025 Internal Linking Opportunities using FattoBoost API (scraped monthly) and enriched with DataForSEO Google Trends data to identify performance timing and trends.

## 2. Data Schemas

### 2.1. User Input Schema (Runtime/UI)
```json
{
  "start_date": "2025-01-01", 
  "end_date": "2025-12-31", 
  "gsc_property": "https://www.ufficiodesignitalia.it/",
  "fattoboost_token": "Bearer <TOKEN>",
  "dataforseo_user": "seo@fattorettosrl.it",
  "dataforseo_pass": "<PASSWORD>",
  "country": "ITA",
  "location_dataforseo": "ITA"
}
```

### 2.2. FattoBoost API Response Schema (Intermediate)
*Source: `POST https://boost.fattorettosrl.it/api/internal_linking_opportunities`*
*Format: JSON*
```json
{
  "success": true,
  "data": [
    {
      "query": "dimensione minima ufficio 2 persone",
      "page": "https://www....",
      "clicks": 2,
      "impressions": 45,
      "average_position": 6.91,
      "ctr": 0.044,
      "search_volume": 20,
      "search_volume_variation": 0.4
      // ... + other fields (potential_*, improved_*)
    }
  ]
}
```

### 2.3. DataForSEO Trends Response Schema (Intermediate)
*Source: `https://api.dataforseo.com/v3/keywords_data/google_trends/overview/live`*
*We need to map this to our needs.*

### 2.4. Final Payload Schema (Excel .xlsx)
**Structure:** 13 Sheets (12 Months + 1 Summary)

**Monthly Sheets (e.g., "Gen 2025"):**
- Raw columns from FattoBoost: `query`, `page`, `clicks`, `impressions`, `ctr`, `position`, `search_volume`, etc.

**Summary Sheet:**
- `query` (Unique)
- `tot_clicks` (Sum)
- `tot_impressions` (Sum)
- `avg_ctr` (Weighted Avg)
- `avg_position` (Avg)
- `first_click_month` (e.g., "Gen 2025")
- `peak_click_month` (e.g., "Mar 2025")
- `last_click_month` (e.g., "Dic 2025")
- `trend_7d` (DataForSEO)
- `trend_30d` (DataForSEO)
- `trend_90d` (DataForSEO)
- `trend_1y` (DataForSEO)
- `rising_related` (DataForSEO)

## 3. Behavioral Rules
1.  **Sequential FattoBoost Calls:** Execute 12 calls (Jan-Dec 2025). If one fails, log error and continue to next month. Do NOT crash.
2.  **Rate Limiting:** DataForSEO calls must be rate-limited (e.g., sleep between calls) to avoid 429 errors.
3.  **Credential Safety:** NO credentials in code or files. Pass via function arguments only.
4.  **UI Feedback:** Must provide progress updates (e.g., "Processing Month 1/12...").
5.  **Configurability:** Params like `country` must be variable.

## 4. Architectural Invariants
- **Layer 1 (Architecture):** `architecture/controller.md` defines the flow.
- **Layer 3 (Tools):**
    - `tools/fetch_fattoboost.py`: Returns DataFrame or Dict for a single month.
    - `tools/fetch_trends.py`: Returns trends for a list of queries.
    - `tools/generate_excel.py`: Compiles the final report.
- **State:** In-memory lists/DataFrames during execution.

## 5. Maintenance Log
- [2026-02-18]: Defined Schemas from `output_json_example.json`.
