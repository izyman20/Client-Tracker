"""
pipeline_tracker.py

Small CLI on top of the SQLite pipeline database. Run it with no arguments
to see a full snapshot, or pass a report name to run just one report.

Usage:
    python pipeline_tracker.py              # run all reports
    python pipeline_tracker.py funnel       # pipeline funnel by stage
    python pipeline_tracker.py stalled      # stalled leads (14+ days)
    python pipeline_tracker.py renewal      # renewal rate by cohort
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "pipeline.db"
QUERIES_DIR = Path(__file__).parent / "queries"


def get_connection():
    if not DB_PATH.exists():
        sys.exit("No database found. Run `python generate_mock_data.py` first.")
    return sqlite3.connect(DB_PATH)


def print_table(headers, rows):
    if not rows:
        print("  (no rows)")
        return
    widths = [max(len(str(h)), max(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


def run_funnel(conn):
    print("\n=== Pipeline Funnel (current stage counts) ===")
    rows = conn.execute(
        """SELECT stage, COUNT(*) AS clients
           FROM clients
           GROUP BY stage
           ORDER BY CASE stage
               WHEN 'Lead' THEN 1 WHEN 'Contacted' THEN 2
               WHEN 'Signed' THEN 3 WHEN 'Renewed' THEN 4 ELSE 5 END"""
    ).fetchall()
    print_table(["Stage", "Clients"], rows)


def run_stalled(conn):
    print("\n=== Stalled Leads (14+ days without progress) ===")
    sql = (QUERIES_DIR / "stalled_leads.sql").read_text()
    rows = conn.execute(sql).fetchall()
    print_table(
        ["ID", "Family", "School", "Sport", "Source", "Stage", "Last Updated", "Days Stalled"],
        rows,
    )


def run_renewal(conn):
    print("\n=== Renewal Rate by Cohort ===")
    sql = (QUERIES_DIR / "renewal_rate_by_cohort.sql").read_text()
    rows = conn.execute(sql).fetchall()
    print_table(["Cohort", "Signed or Renewed", "Renewed", "Renewal Rate %"], rows)


REPORTS = {
    "funnel": run_funnel,
    "stalled": run_stalled,
    "renewal": run_renewal,
}


def main():
    conn = get_connection()
    arg = sys.argv[1] if len(sys.argv) > 1 else None

    if arg and arg not in REPORTS:
        sys.exit(f"Unknown report '{arg}'. Options: {', '.join(REPORTS)}")

    if arg:
        REPORTS[arg](conn)
    else:
        for report in REPORTS.values():
            report(conn)

    conn.close()


if __name__ == "__main__":
    main()
