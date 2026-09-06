-- renewal_rate_by_cohort.sql
-- For each cohort (season), calculates what share of clients who reached
-- "Signed" or beyond went on to "Renewed" in a later season.

SELECT
    cohort,
    COUNT(*) AS total_signed_or_renewed,
    SUM(CASE WHEN stage = 'Renewed' THEN 1 ELSE 0 END) AS renewed_count,
    ROUND(
        100.0 * SUM(CASE WHEN stage = 'Renewed' THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS renewal_rate_pct
FROM clients
WHERE stage IN ('Signed', 'Renewed')
GROUP BY cohort
ORDER BY cohort;
