SELECT
  s.name AS sport,
  SUM(CASE WHEN pi.medal = 'Gold' THEN 1 ELSE 0 END)   AS golds,
  SUM(CASE WHEN pi.medal = 'Silver' THEN 1 ELSE 0 END) AS silvers,
  SUM(CASE WHEN pi.medal = 'Bronze' THEN 1 ELSE 0 END) AS bronzes,
  SUM(CASE WHEN pi.medal IS NOT NULL AND pi.medal <> 'NA' THEN 1 ELSE 0 END) AS total_medals
FROM PARTICIPATED_IN pi
JOIN EVENT e   ON e.event_id = pi.event_id
JOIN SPORT s   ON s.sport_id = e.sport_id
GROUP BY s.name
HAVING total_medals > 0
ORDER BY total_medals DESC, s.name;
