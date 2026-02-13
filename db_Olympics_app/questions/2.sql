SELECT
  t.team_id,
  t.name AS team_name,
  t.noc,
  SUM(CASE WHEN pi.medal IS NOT NULL AND pi.medal <> 'NA' THEN 1 ELSE 0 END) AS medals
FROM TEAM t
JOIN IN_THE_TEAM it ON it.team_id = t.team_id
JOIN PARTICIPATED_IN pi ON pi.athlete_id = it.athlete_id
GROUP BY t.team_id, t.name, t.noc
HAVING medals > 0
ORDER BY medals DESC, team_name
LIMIT 10;
