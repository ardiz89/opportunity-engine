# Findings & Research

## Research Log
- **[2026-02-18] Schema Definition:**
  - Analyzed `output_json_example.json`.
  - Confirmed FattoBoost returns a flat list of SEO metrics.
  - Confirmed need to calculate "Start/Peak/End" months post-aggregation.

## Constraints
- **Sequential API:** FattoBoost calls must be one-by-one to avoid overload or logic issues.
- **DataForSEO Cost:** Trends API has costs; user implied "safe rate limiting".
- **Credentials:** STRICTLY In-Memory.
