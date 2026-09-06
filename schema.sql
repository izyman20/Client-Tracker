-- schema.sql
-- Core schema for the Client Pipeline Tracker.
-- Models a youth sports enrollment pipeline: Lead -> Contacted -> Signed -> Renewed
-- (with "Lost" as a terminal drop-off stage).

DROP TABLE IF EXISTS stage_history;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    client_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    family_name     TEXT NOT NULL,
    school          TEXT NOT NULL,
    sport           TEXT NOT NULL CHECK (sport IN ('Flag Football', 'Basketball')),
    lead_source     TEXT NOT NULL,       -- e.g. Referral, School Flyer, Social Media, Walk-up
    cohort          TEXT NOT NULL,       -- season the client entered, e.g. 'Fall 2024'
    stage           TEXT NOT NULL CHECK (stage IN ('Lead', 'Contacted', 'Signed', 'Renewed', 'Lost')),
    date_entered    TEXT NOT NULL,       -- ISO date client entered the pipeline
    last_updated    TEXT NOT NULL        -- ISO date of most recent stage change
);

-- Every stage transition a client goes through, so we can measure how long
-- a client sat in a stage (used for the "stalled lead" query).
CREATE TABLE stage_history (
    history_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id       INTEGER NOT NULL REFERENCES clients(client_id),
    stage           TEXT NOT NULL,
    changed_on      TEXT NOT NULL
);

CREATE INDEX idx_clients_stage ON clients(stage);
CREATE INDEX idx_clients_cohort ON clients(cohort);
CREATE INDEX idx_history_client ON stage_history(client_id);
