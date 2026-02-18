
import streamlit as st
import pandas as pd
import sys
import os
import time
from datetime import datetime, date

# Add current directory to path so we can import tools
sys.path.append(os.getcwd())

from tools.fattoboost_client import fetch_fattoboost_month
from tools.dataforseo_client import fetch_keyword_trends
from tools.report_builder import generate_report

st.set_page_config(page_title="Opportunity Engine 2025", layout="wide")

st.title("🚀 Opportunity Engine 2025")

with st.expander("📚 Guida all'uso (Tutorial)", expanded=True):
    st.markdown("""
    ### Come funziona questo strumento
    
    Questo software automatizza il processo di analisi delle opportunità di Internal Linking per l'anno 2025 e le arricchisce con i dati di trend di ricerca.
    
    #### 1️⃣ Configurazione
    *   Inserisci il **Token FattoBoost** e le credenziali **DataForSEO** nella barra laterale.
    *   Specifica la **Proprietà GSC** (es. `sc-domain:tuosito.it` o `https://tuosito.it/`).
    *   Seleziona il Paese target (es. `ITA`).
    
    #### 2️⃣ Estrazione Dati (Fase 1)
    *   Clicca su **"Avvia Estrazione"**.
    *   Il sistema interrogherà le API di FattoBoost per ogni mese del 2025 (Gennaio - Dicembre).
    *   Potrai seguire il progresso nel log dettagliato.
    
    #### 3️⃣ Selezione Query (Fase 2)
    *   Al termine dell'estrazione, apparirà una tabella con tutte le query univoche trovate.
    *   Puoi **selezionare/deselezionare** le query per cui desideri ottenere i dati di Google Trends (DataForSEO).
    
    #### 4️⃣ Report Finale (Fase 3)
    *   Clicca su **"Arricchisci e Genera Report"**.
    *   Il sistema scaricherà i trend per le query selezionate e genererà un file Excel.
    *   Scarica il file che conterrà:
        *   12 tab mensili con i dati grezzi.
        *   1 tab di **Riepilogo** con metriche aggregate (Clic Totali, Mese Primo Clic, Mese Picco, Trend 7/30gg).
    """)

# --- Sidebar Inputs ---
st.sidebar.header("Configurazione")

# 1. Credentials
fattoboost_token = st.sidebar.text_input("FattoBoost Bearer Token", type="password")
dataforseo_user = st.sidebar.text_input("DataForSEO Username", value="seo@fattorettosrl.it")
dataforseo_pass = st.sidebar.text_input("DataForSEO Password", type="password")

# 2. Target Properties
gsc_property = st.sidebar.text_input("Proprietà GSC", value="sc-domain:naturasi.it", help="es. https://example.com/ o sc-domain:example.com")

# 3. Settings
country = st.sidebar.selectbox("Paese", ["ITA", "USA", "UK"])
analyze_trends = st.sidebar.checkbox("Arricchisci con Trends (DataForSEO)", value=True)

# --- Main Logic ---

def extract_domain(prop_url):
    # Simple extraction logic
    s = prop_url.replace("sc-domain:", "").replace("https://", "").replace("http://", "")
    if "/" in s:
        s = s.split("/")[0]
    return s

# Session State Initialization
if "monthly_data" not in st.session_state:
    st.session_state.monthly_data = {}
if "unique_queries" not in st.session_state:
    st.session_state.unique_queries = []
if "step" not in st.session_state:
    st.session_state.step = 1 # 1: Config, 2: Review/Select, 3: Processing Trends

# Step 1: Configuration & Start
if st.session_state.step == 1:
    start_process = st.button("Avvia Estrazione (FattoBoost)")

    if start_process:
        if not fattoboost_token or not gsc_property:
            st.error("Per favore inserisci il Token FattoBoost e la Proprietà GSC.")
            st.stop()
        
        # Derby property pattern from GSC property
        derived_pattern = extract_domain(gsc_property)
        
        st.info(f"Avvio analisi per: **{gsc_property}** (Anno 2025)")
        st.caption(f"Pattern proprietà rilevato: {derived_pattern}")
        
        # Progress Containers
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_area = st.empty()
        
        logs = []
        def log(msg):
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
            log_area.code("\n".join(logs[-10:])) # Show last 10 logs

        # 1. Fetch Monthly Data
        monthly_data = {}
        months = [
            ("Gen 2025", "2025-01-01", "2025-01-31"),
            ("Feb 2025", "2025-02-01", "2025-02-28"),
            ("Mar 2025", "2025-03-01", "2025-03-31"),
            ("Apr 2025", "2025-04-01", "2025-04-30"),
            ("Mag 2025", "2025-05-01", "2025-05-31"),
            ("Giu 2025", "2025-06-01", "2025-06-30"),
            ("Lug 2025", "2025-07-01", "2025-07-31"),
            ("Ago 2025", "2025-08-01", "2025-08-31"),
            ("Set 2025", "2025-09-01", "2025-09-30"),
            ("Ott 2025", "2025-10-01", "2025-10-31"),
            ("Nov 2025", "2025-11-01", "2025-11-30"),
            ("Dic 2025", "2025-12-01", "2025-12-31"),
        ]
        
        total_months = len(months)
        current_idx = 0
        
        all_queries_set = set()
        
        for month_name, start_d, end_d in months:
            status_text.text(f"Scaricamento dati per {month_name}...")
            log(f"Richiesta {month_name} ({start_d} - {end_d})...")
            
            try:
                records = fetch_fattoboost_month(
                    token=fattoboost_token,
                    start_date=start_d,
                    end_date=end_d,
                    property_url=gsc_property,
                    property_pattern=derived_pattern,
                    show_keywords="nobrand",
                    country=country,
                    log_callback=log
                )
                
                if records:
                    monthly_data[month_name] = records
                    # Collect unique queries
                    for r in records:
                        if 'query' in r:
                            all_queries_set.add(r['query'])
                    log(f"✅ {month_name}: {len(records)} record trovati.")
                else:
                    log(f"⚠️ {month_name}: Nessun dato restituito (o errore gestito).")
                    
            except Exception as e:
                log(f"❌ Errore in {month_name}: {str(e)}")
                
            current_idx += 1
            progress_bar.progress(current_idx / total_months)
            time.sleep(1) # Brief pause to be nice to API
            
        # Store in session state
        st.session_state.monthly_data = monthly_data
        st.session_state.unique_queries = sorted(list(all_queries_set))
        st.session_state.step = 2
        st.rerun()

# Step 2: Review & Select
elif st.session_state.step == 2:
    st.success(f"✅ Estrazione Completata! Trovate {len(st.session_state.unique_queries)} query univoche.")
    
    st.subheader("Seleziona Query per Analisi Trends")
    st.markdown("Seleziona le query per cui vuoi ottenere i dati di Google Trends. In questa tabella sono mostrate le metriche aggregate per l'anno 2025.")
    
    # 1. Aggregate Data from Session State
    all_records = []
    for month, records in st.session_state.monthly_data.items():
        all_records.extend(records)
    
    if all_records:
        full_df = pd.DataFrame(all_records)
        # Ensure numeric types
        cols_to_numeric = ['clicks', 'impressions', 'average_position', 'ctr']
        for c in cols_to_numeric:
            full_df[c] = pd.to_numeric(full_df[c], errors='coerce').fillna(0)

        # Grouping
        df_grouped = full_df.groupby('query').agg({
            'clicks': 'sum',
            'impressions': 'sum',
            'average_position': 'mean',
            'ctr': 'mean' 
        }).reset_index()
        
        # Rounding for display
        df_grouped['average_position'] = df_grouped['average_position'].round(1)
        df_grouped['ctr'] = df_grouped['ctr'].round(4)
        
        # Add Checkbox
        df_grouped.insert(0, "Analizza", True)
        
        # Renaming for UI (Italian)
        df_grouped = df_grouped.rename(columns={
            'query': 'Query',
            'clicks': 'Click Totali',
            'impressions': 'Impression Totali',
            'average_position': 'Pos. Media',
            'ctr': 'CTR Medio'
        })
        
        # Display using data_editor
        edited_df = st.data_editor(
            df_grouped,
            column_config={
                "Analizza": st.column_config.CheckboxColumn(
                    "Analizza?",
                    help="Seleziona per scaricare dati Google Trends",
                    default=True,
                ),
                "CTR Medio": st.column_config.NumberColumn(
                    "CTR Medio",
                    format="%.4f"
                ),
                "Click Totali": st.column_config.NumberColumn("Click Totali"),
                "Impression Totali": st.column_config.NumberColumn("Impression Totali"),
                "Pos. Media": st.column_config.NumberColumn("Pos. Media", format="%.1f"),
            },
            disabled=["Query", "Click Totali", "Impression Totali", "Pos. Media", "CTR Medio"],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("Nessun dato trovato da aggregare.")
        edited_df = pd.DataFrame(columns=["Analizza", "Query"])

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Arricchisci e Genera Report"):
            # Filter based on Checkbox
            if not edited_df.empty:
                selected_queries = edited_df[edited_df["Analizza"] == True]["Query"].tolist()
            else:
                selected_queries = []
                
            st.session_state.selected_queries = selected_queries
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Salta Trends (Solo Report)"):
            st.session_state.selected_queries = []
            st.session_state.step = 3
            st.rerun()

# Step 3: Enrich & Build
elif st.session_state.step == 3:
    st.info("Elaborazione Trends e Generazione Report in corso...")
    
    selected_queries = st.session_state.selected_queries
    monthly_data = st.session_state.monthly_data
    
    # Progress Containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_area = st.empty()
    
    logs = []
    def log(msg):
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        log_area.code("\n".join(logs[-10:]))
    
    # 2. Trends Analysis
    trends_results = {}
    if selected_queries and analyze_trends:
        status_text.text(f"Scaricamento Trends per {len(selected_queries)} query...")
        log(f"Avvio Analisi Trends per {len(selected_queries)} query selezionate...")
        
        # Define callback
        total_q = len(selected_queries)
        def update_trends_progress(current, total, msg):
             # Map 0-1 to progress bar
             progress_bar.progress(current / total)
             status_text.text(f"Trends: {current}/{total} - {msg}")
            
        try:
            trends_results = fetch_keyword_trends(
                selected_queries, 
                dataforseo_user, 
                dataforseo_pass, 
                location_code=2380, # Italy fixed for now
                progress_callback=update_trends_progress
            )
            log(f"✅ Trends raccolti per {len(trends_results)} query.")
        except Exception as e:
            log(f"❌ Errore scaricamento trends: {e}")
            
    # 3. Report Generation
    status_text.text("Generazione File Excel...")
    progress_bar.progress(1.0)
    
    output_file = f"Report_{gsc_property.replace(':','_').replace('/','_')}_2025.xlsx"
    full_path = os.path.join(os.getcwd(), output_file)
    
    try:
        final_path = generate_report(monthly_data, trends_results, output_path=full_path)
        log(f"✅ Report salvato in {final_path}")
        
        with open(final_path, "rb") as f:
            st.download_button(
                label="📥 Scarica Report Excel Finale",
                data=f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        st.success("Analisi Completata!")
        
        if st.button("Avvia Nuova Analisi"):
            for key in ["monthly_data", "unique_queries", "step", "selected_queries"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
    except Exception as e:
        log(f"❌ Errore generazione report: {e}")
        st.error(f"Impossibile generare il report: {e}")

