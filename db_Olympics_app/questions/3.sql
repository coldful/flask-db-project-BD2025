SELECT
  s.sport_id,
  s.name AS sport,
  COUNT(e.event_id) AS event_count
FROM SPORT s
LEFT JOIN EVENT e ON e.sport_id = s.sport_id
GROUP BY s.sport_id, s.name
ORDER BY event_count DESC, sport;
