# Client Pipeline Tracker

A SQLite-backed CRM tool that tracks clients through a sales pipeline —
**Lead → Contacted → Signed → Renewed** — built to mirror the enrollment
workflow I run as Field Director for a youth sports program (4 partner
schools, flag football and basketball).

The dataset here is realistic mock data (fictional family names, real
program patterns), generated with `generate_mock_data.py`.

## What it does

- Models a multi-season enrollment pipeline in SQLite
- Tracks every stage transition per client in a `stage_history` table
- Ships two SQL reports used to run the actual program:
  - **Stalled leads** — auto-flags any client stuck in `Lead` or `Contacted`
    for 14+ days so staff know who to follow up with
  - **Renewal rate by cohort** — calculates what % of each season's signed
    clients renewed the following season
- A small CLI (`pipeline_tracker.py`) to run any report, or all of them

## Project structure

```
client-pipeline-tracker/
├── schema.sql                     # table definitions
├── generate_mock_data.py          # builds pipeline.db with realistic mock data
├── pipeline_tracker.py            # CLI entry point
├── queries/
│   ├── stalled_leads.sql
│   └── renewal_rate_by_cohort.sql
└── data/
    └── pipeline.db                # generated, not committed
```

## Running it

```bash
pip install -r requirements.txt   # no external deps beyond the stdlib, kept for clarity
python generate_mock_data.py      # builds data/pipeline.db
python pipeline_tracker.py        # runs all reports
python pipeline_tracker.py stalled    # or just one: funnel | stalled | renewal
```

## Why I built this

I've run client relationships for Neighborhood Sports Training end-to-end —
from first contact through signup and renewal — for three years, growing
the program from 150 to 400+ enrolled families. This project models that
workflow in SQL so I could practice the queries a real CRM would need:
finding leads that are going cold, and measuring renewal rate season over
season instead of eyeballing a spreadsheet.
