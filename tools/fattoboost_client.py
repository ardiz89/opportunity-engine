
import requests
import time
import logging

def fetch_fattoboost_month(token, start_date, end_date, property_url, property_pattern, show_keywords="nobrand", country="ITA", location="ITA", log_callback=None):
    """
    Fetches internal linking opportunities for a specific date range.
    """
    url = "https://boost.fattorettosrl.it/api/internal_linking_opportunities"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "dateRangeStart": start_date,
        "dateRangeEnd": end_date,
        "searchConsoleProperty": property_url,
        "country": [country], 
        "locationDataForSEO": location,
        "propertyPattern": property_pattern,
        "showKeywords": show_keywords,
        "excluded_queries": []
    }
    
    msg = f"[*] Fetching FattoBoost data for {start_date} to {end_date}..."
    if log_callback: log_callback(msg)
    else: print(msg)
    
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=27100)  # Long timeout for data processing
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    records = data.get("data", [])
                    msg = f"    [OK] Retrieved {len(records)} records."
                    if log_callback: log_callback(msg)
                    else: print(msg)
                    return records
                else:
                    msg = f"    [ERROR] API Success=False: {data.get('message')}"
                    if log_callback: log_callback(msg)
                    else: print(msg)
                    # If validation error, retrying won't help -> return empty
                    return []
            elif response.status_code == 401:
                msg = "    [CRITICAL] Unauthorized (401). Check Token."
                if log_callback: log_callback(msg)
                else: print(msg)
                raise Exception("Invalid Token")
            elif response.status_code == 429:
                msg = f"    [WARN] Rate Limited. Waiting {2**attempt}s..."
                if log_callback: log_callback(msg)
                else: print(msg)
                time.sleep(2**attempt)
            else:
                msg = f"    [ERROR] Status {response.status_code}: {response.text[:200]}"
                if log_callback: log_callback(msg)
                else: print(msg)
                time.sleep(2**attempt)
                
        except requests.exceptions.RequestException as e:
            msg = f"    [ERROR] Network error: {e}"
            if log_callback: log_callback(msg)
            else: print(msg)
            time.sleep(2**attempt)

    msg = "    [FAIL] Max retries reached for this month."
    if log_callback: log_callback(msg)
    else: print(msg)
    return []

if __name__ == "__main__":
    # Test execution
    import sys
    if len(sys.argv) > 3:
        token = sys.argv[1]
        prop = sys.argv[2] 
        pattern = sys.argv[3]
        fetch_fattoboost_month(token, "2025-01-01", "2025-01-31", prop, pattern, show_keywords="nobrand")
