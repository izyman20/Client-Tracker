-- stalled_leads.sql
-- Flags any client sitting in "Lead" or "Contacted" for more than 14 days
-- without moving forward, so staff know who to follow up with.

SELECT
    c.client_id,
    c.family_name,
    c.school,
    c.sport,
    c.lead_source,
    c.stage,
    c.last_updated,
    CAST(julianday('now') - julianday(c.last_updated) AS INTEGER) AS days_since_update
FROM clients c
WHERE c.stage IN ('Lead', 'Contacted')
  AND CAST(julianday('now') - julianday(c.last_updated) AS INTEGER) > 14
ORDER BY days_since_update DESC;
