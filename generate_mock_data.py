"""
generate_mock_data.py

Builds pipeline.db (SQLite) and populates it with realistic mock data modeled
on a multi-season youth sports enrollment pipeline: 4 partner schools, two
sports, several lead sources, and a handful of enrollment cohorts (seasons).

All names are fictional. Patterns (renewal rate, lead sources, growth across
cohorts) are modeled after a real program but the numbers are synthetic.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "pipeline.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

random.seed(42)

SCHOOLS = ["Cypress Ridge Elementary", "Katy Oaks Elementary", "Willow Creek Elementary", "Mason Trails Elementary"]
SPORTS = ["Flag Football", "Basketball"]
LEAD_SOURCES = ["Referral", "School Flyer", "Social Media", "Walk-up", "Returning Family"]

# Cohorts in chronological order, each with a target new-lead volume that
# grows over time (mirrors 150 -> 400+ family growth).
COHORTS = [
    ("Fall 2023", date(2023, 8, 15), 55),
    ("Spring 2024", date(2024, 1, 10), 60),
    ("Fall 2024", date(2024, 8, 12), 90),
    ("Spring 2025", date(2025, 1, 8), 110),
    ("Fall 2025", date(2025, 8, 11), 130),
]

FIRST_NAMES = ["Aaliyah", "Marcus", "Sofia", "Jayden", "Emma", "Noah", "Camila", "Elijah", "Zoe", "Liam",
               "Amara", "Mateo", "Harper", "Kai", "Isabella", "Xavier", "Layla", "Josiah", "Nadia", "Deion",
               "Priya", "Andre", "Maya", "Chloe", "Tyrell", "Gianna", "Malik", "Ruby", "Isaac", "Simone"]
LAST_NAMES = ["Johnson", "Garcia", "Williams", "Brown", "Davis", "Martinez", "Robinson", "Clark", "Lewis",
              "Walker", "Young", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Green", "Adams", "Baker"]


def random_family_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def build_client_rows():
    """Simulate each cohort moving through the pipeline over time."""
    clients = []
    history = []
    client_id = 1
    today = date(2026, 9, 1)

    for cohort_idx, (cohort_name, cohort_start, new_leads) in enumerate(COHORTS):
        is_most_recent = cohort_idx == len(COHORTS) - 1
        is_prior_cohort_exists = cohort_idx > 0

        for _ in range(new_leads):
            entered = cohort_start + timedelta(days=random.randint(0, 20))
            school = random.choice(SCHOOLS)
            sport = random.choice(SPORTS)
            source = random.choices(LEAD_SOURCES, weights=[35, 25, 15, 10, 15])[0]

            # Determine how far this client progressed.
            # Older cohorts have had time to fully resolve; the newest cohort
            # still has some clients sitting in early stages.
            roll = random.random()
            if is_most_recent:
                # newest cohort: pipeline still actively moving
                if roll < 0.12:
                    stage = "Lead"
                elif roll < 0.30:
                    stage = "Contacted"
                elif roll < 0.85:
                    stage = "Signed"
                else:
                    stage = "Lost"
            else:
                if roll < 0.08:
                    stage = "Lost"
                elif source == "Returning Family" and is_prior_cohort_exists and random.random() < 0.8:
                    stage = "Renewed"
                elif random.random() < 0.70:
                    stage = "Renewed" if is_prior_cohort_exists and random.random() < 0.55 else "Signed"
                else:
                    stage = "Signed"

            # Stage history: simulate realistic gaps between stage changes
            stage_order = ["Lead", "Contacted", "Signed", "Renewed"]
            reached = stage_order[: stage_order.index(stage) + 1] if stage in stage_order else ["Lead", "Contacted"]

            last_change = entered
            for i, s in enumerate(reached):
                if i == 0:
                    changed_on = entered
                else:
                    gap = random.randint(2, 12) if s != "Signed" else random.randint(3, 18)
                    changed_on = last_change + timedelta(days=gap)
                last_change = changed_on
                history.append((client_id, s, changed_on.isoformat()))

            if stage == "Lost":
                lost_after = random.randint(5, 25)
                last_change = entered + timedelta(days=lost_after)
                history.append((client_id, "Lost", last_change.isoformat()))

            # Don't let last_updated be in the future relative to "today"
            if last_change > today:
                last_change = today

            clients.append((
                client_id,
                random_family_name(),
                school,
                sport,
                source,
                cohort_name,
                stage,
                entered.isoformat(),
                last_change.isoformat(),
            ))
            client_id += 1

    return clients, history


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    clients, history = build_client_rows()

    conn.executemany(
        """INSERT INTO clients
           (client_id, family_name, school, sport, lead_source, cohort, stage, date_entered, last_updated)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        clients,
    )
    conn.executemany(
        "INSERT INTO stage_history (client_id, stage, changed_on) VALUES (?, ?, ?)",
        history,
    )
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
    print(f"Generated {total} mock client records across {len(COHORTS)} cohorts.")
    print(f"Database written to: {DB_PATH}")
    conn.close()


if __name__ == "__main__":
    main()
