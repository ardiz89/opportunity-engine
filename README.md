# Opportunity Engine 2025

This tool automates the extraction and analysis of Internal Linking Opportunities for 2025.

## Features
- **Data Source:** FattoBoost API (Monthly internal linking data).
- **Enrichment:** DataForSEO Google Trends (Trend slope, rising associated queries).
- **Output:** Multi-tab Excel report with Summary of Start/Peak/End months.
- **UI:** Streamlit Web App with live progress tracking.

## Pre-requisites
- Python 3.9+
- FattoBoost Bearer Token
- DataForSEO Credentials

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Run the application using Streamlit:
```bash
streamlit run app.py
```

## Architecture
- `tools/`: Python scripts for API calls and report building.
- `app.py`: Main controller and UI.
