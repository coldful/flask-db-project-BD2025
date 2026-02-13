SELECT
  a.athlete_id,
  a.name AS athlete_name,
  SUM(CASE WHEN pi.medal IS NOT NULL AND pi.medal <> 'NA' THEN 1 ELSE 0 END) AS medals
FROM ATHLETE a
JOIN PARTICIPATED_IN pi ON pi.athlete_id = a.athlete_id
GROUP BY a.athlete_id, a.name
HAVING medals > 0
ORDER BY medals DESC, athlete_name
LIMIT 10;
