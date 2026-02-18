
import requests
import time
from datetime import datetime, timedelta

def fetch_keyword_trends(keywords, username, password, location_code=2380, date_from="2024-01-01", date_to="2024-12-31", progress_callback=None):
    """
    Fetches Google Trends data for a list of keywords using DataForSEO Live API.
    Returns a dictionary: { keyword: { 'trend_7d': ..., 'trend_30d': ..., 'rising': ... } }
    progress_callback: Function accepting (current_index, total_count, message)
    """
    url = "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live"
    results = {}
    total = len(keywords)
    
    print(f"[*] Fetching Trends for {total} keywords...")
    
    for i, kw in enumerate(keywords):
        if i > 0 and i % 10 == 0:
            print(f"    Progress: {i}/{total}")
            
        if progress_callback:
            progress_callback(i, total, f"Fetching trend for: {kw}")
            
        payload = [{
            "keywords": [kw],
            "location_code": location_code,
            "language_code": "it",
            "date_from": date_from,
            "date_to": date_to
        }]
        
        try:
            response = requests.post(url, json=payload, auth=(username, password), timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data['status_code'] == 20000:
                    tasks = data.get('tasks', [])
                    if tasks:
                        result_items = tasks[0].get('result', [])
                        if result_items:
                            item = result_items[0].get('items', [])
                            if item:
                                ts_data = item
                                results[kw] = analyze_trend(ts_data)
                            else:
                                results[kw] = {"trend": "No Data"}
                else:
                    print(f"    [ERROR] API Error for '{kw}': {data['status_message']}")
            elif response.status_code == 429:
                print("    [WARN] Rate limit hit. Sleeping 5s.")
                if progress_callback:
                    progress_callback(i, total, "Rate limited and sleeping...")
                time.sleep(5)
            
            time.sleep(0.5) 
            
        except Exception as e:
            print(f"    [ERROR] Exception for '{kw}': {e}")
            
    if progress_callback:
        progress_callback(total, total, "Trends Fetch Complete")
        
    return results

def analyze_trend(ts_data):
    """
    Analyzes the time series data to extract 7d, 30d, etc. trends.
    Expects ts_data to be list of dicts with 'date_from', 'date_to', 'values' (list of integers).
    """
    if not ts_data:
        return {}
        
    # Sort by date just in case
    # Assuming standard format
    
    # Simple extraction (mock logic needs refinement based on actual JSON shape)
    # The API returns 'values': [relative_search_volume]
    
    # Calculate simple slope or avg of last few points
    last_val = ts_data[-1]['values'][0] if ts_data[-1].get('values') else 0
    first_val = ts_data[0]['values'][0] if ts_data[0].get('values') else 0
    
    return {
        "last_value": last_val,
        "year_trend": "Up" if last_val > first_val else "Down",
        "data_points": len(ts_data)
    }

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 2:
        u = sys.argv[1]
        p = sys.argv[2]
        res = fetch_keyword_trends(["ufficio design"], u, p, date_from="2025-01-01", date_to="2025-01-31")
        print(res)
