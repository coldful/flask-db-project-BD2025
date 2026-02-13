SELECT
  t.noc,
  t.name AS team_name,
  COUNT(DISTINCT e.sport_id) AS sports_count
FROM TEAM t
JOIN IN_THE_TEAM it       ON it.team_id = t.team_id
JOIN PARTICIPATED_IN pi   ON pi.athlete_id = it.athlete_id
JOIN EVENT e              ON e.event_id = pi.event_id
GROUP BY t.noc, t.name
ORDER BY sports_count DESC, team_name
LIMIT 10;
