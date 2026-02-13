SELECT
  e.event_id,
  e.name AS event_name,
  s.name AS sport,
  o.year,
  o.season,
  o.city,
  COUNT(pi.athlete_id) AS medalists
FROM EVENT e
JOIN SPORT s ON s.sport_id = e.sport_id
JOIN OLYMPICS o ON o.olympics_id = e.olympics_id
LEFT JOIN PARTICIPATED_IN pi ON pi.event_id = e.event_id
GROUP BY e.event_id, e.name, s.name, o.year, o.season, o.city
ORDER BY medalists DESC, event_name
LIMIT 10;
