
import pandas as pd
from datetime import datetime
import os

def generate_report(monthly_data, trends_data, output_path="c:/Users/undrg/Opportunities/Opportunities_Report.xlsx"):
    """
    Generates the Excel report with monthly tabs and a summary tab.
    monthly_data: Dict { "Jan 2025": [records], ... }
    trends_data: Dict { query: trend_info }
    """
    print(f"[*] Generating Excel Report at {output_path}...")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        all_records = []
        
        # 1. Create Monthly Sheets
        for month_name, records in monthly_data.items():
            if not records:
                continue
                
            df = pd.DataFrame(records)
            if df.empty:
                continue
                
            # Add Month column for aggregation later
            # Add Month column for aggregation later
            df['_month_name'] = month_name
            
            # Helper to parse Italian months if needed, or fallback
            # Mapping Italian -> English for strptime
            it_to_en = {
                "Gen": "Jan", "Feb": "Feb", "Mar": "Mar", "Apr": "Apr", "Mag": "May", "Giu": "Jun",
                "Lug": "Jul", "Ago": "Aug", "Set": "Sep", "Ott": "Oct", "Nov": "Nov", "Dic": "Dec"
            }
            
            clean_name = month_name
            for it, en in it_to_en.items():
                if month_name.startswith(it):
                    clean_name = month_name.replace(it, en)
                    break
            
            df['_month_date'] = pd.to_datetime(clean_name, format='%b %Y', errors='coerce')
            
            # Select relevant columns for the sheet (remove internal ones if needed)
            cols_to_save = [c for c in df.columns if not c.startswith('_')]
            
            sheet_name = month_name[:31] # Excel limit
            df[cols_to_save].to_excel(writer, sheet_name=sheet_name, index=False)
            
            all_records.extend(df.to_dict('records'))
            
        # 2. Create Summary Sheet
        if all_records:
            master_df = pd.DataFrame(all_records)
            
            # Ensure _month_date is datetime
            master_df['_month_date'] = pd.to_datetime(master_df['_month_date'])
            
            # Define aggregation logic
            summary_list = []
            
            grouped = master_df.groupby('query')
            
            for query, group in grouped:
                # Basic metrics
                total_clicks = group['clicks'].sum()
                total_impressions = group['impressions'].sum()
                avg_pos = group['average_position'].mean()
                avg_ctr = group['ctr'].mean()
                max_vol = group['search_volume'].max()
                
                # Time-based metrics
                # Sort by date
                sorted_group = group.sort_values('_month_date')
                
                clicks_only = sorted_group[sorted_group['clicks'] > 0]
                
                first_click_month = "N/A"
                last_click_month = "N/A"
                peak_month = "N/A"
                
                if not clicks_only.empty:
                    # Check for NaT before formatting
                    f_date = clicks_only.iloc[0]['_month_date']
                    l_date = clicks_only.iloc[-1]['_month_date']
                    
                    if pd.notnull(f_date):
                        first_click_month = f_date.strftime('%b %Y')
                    if pd.notnull(l_date):
                        last_click_month = l_date.strftime('%b %Y')
                
                # Peak Month
                # Month with max clicks
                peak_idx = sorted_group['clicks'].idxmax()
                peak_row = sorted_group.loc[peak_idx]
                p_date = peak_row['_month_date']
                
                if pd.notnull(p_date):
                    peak_month = p_date.strftime('%b %Y')
                
                record = {
                    'Query': query,
                    'Total Clicks': total_clicks,
                    'Total Impressions': total_impressions,
                    'Avg Position': avg_pos,
                    'Avg CTR': avg_ctr,
                    'Max Search Volume': max_vol,
                    'First Click Month': first_click_month,
                    'Peak Click Month': peak_month,
                    'Last Click Month': last_click_month
                }
                
                # Integrate Trends
                if query in trends_data:
                     t = trends_data[query]
                     # Flatten trend dict
                     # e.g. { 'trend_7d': ..., 'rising': ... }
                     for k, v in t.items():
                         record[f"Trend {k}"] = v
                
                summary_list.append(record)
            
            summary_df = pd.DataFrame(summary_list)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            print("    [OK] Summary sheet created.")
            
        else:
            print("    [WARN] No records found to build report.")
            
    return output_path

if __name__ == "__main__":
    pass
