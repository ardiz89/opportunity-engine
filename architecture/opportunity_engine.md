# Opportunity Engine Architecture

## 1. Overview
The Opportunity Engine responsibilities are:
1.  Iterate through the 12 months of 2025.
2.  Fetch Internal Linking Opportunities from FattoBoost API for each month.
3.  Aggregate data to find unique queries and calculate summary metrics.
4.  Fetch Google Trends data for top unique queries from DataForSEO.
5.  Generate a multi-tab Excel report.

## 2. Component Logic

### 2.1. FattoBoost Fetcher (`tools/fattoboost_client.py`)
- **Input:** `start_date`, `end_date`, `property`, `token`, `country`, `location`, `property_pattern`.
- **Logic:**
    - POST to `https://boost.fattorettosrl.it/api/internal_linking_opportunities`.
    - Handle 401 (Unauthorized) -> Critical Error.
    - Handle 500/Timeout -> Retry 3 times with exponential backoff.
    - Handle 404/Validation -> Log error and skip month (don't crash process).
- **Output:** List of dictionaries (records).

### 2.2. Trends Fetcher (`tools/dataforseo_client.py`)
- **Input:** List of `queries`, `username`, `password`, `location_code` (2380 for Italy).
- **Logic:**
    - Iterate through queries.
    - Apply Rate Limiting: Max 2 requests per second (safe buffer).
    - POST to `https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live`.
    - Extract `interest_over_time` data.
    - Calculate:
        - `Trend 7d`: Last 7 days slope/avg.
        - `Trend 30d`: Last 30 days slope/avg.
        - `Rising Related`: Top rising related query.
- **Output:** Dictionary `{query: {trend_data}}`.

### 2.3. Report Builder (`tools/report_builder.py`)
- **Input:** 
    - `monthly_data`: Dict `{ "Jan 2025": [records], ... }`
    - `trends_data`: Dict `{ query: trend_data }`
- **Logic:**
    - **Monthly Sheets:** Create 12 tabs with raw data.
    - **Summary Sheet:**
        - Group by `query`.
        - Sum `clicks`, `impressions`.
        - Avg `position`, `ctr`.
        - Determine `first_click_month` (Min Month where clicks > 0).
        - Determine `peak_click_month` (Month with Max clicks).
        - Determine `last_click_month` (Max Month where clicks > 0).
        - Join with `trends_data`.
    - **Formatting:** Use Excel styles (Bold headers, Filters).
- **Output:** Path to valid `.xlsx` file.

## 3. Execution Flow (Controller)
1.  **Initialize:** User inputs keys/config.
2.  **Loop Months:** 
    ```python
    scan_results = {}
    for month in [Jan..Dec]:
        try:
            data = fetch_fattoboost(...)
            scan_results[month] = data
        except Exception:
            log_error(month)
            continue
    ```
3.  **Aggregate:** Get list of unique queries.
4.  **Fetch Trends:**
    ```python
    unique_queries = get_top_queries(scan_results, limit=50) # Limit to avoid cost explosion? 
    # USER REQUEST implies all unique queries, but "safe rate limiting" applies.
    # We will process ALL unique queries found in the summary.
    trends = fetch_trends(unique_queries)
    ```
5.  **Build Report:** `generate_excel(scan_results, trends)`

## 4. Error Handling
- **Partial Failure:** If Jan-Nov succeed but Dec fails, report is generated for Jan-Nov.
- **Critical Failure:** If Auth fails, stop immediately.
