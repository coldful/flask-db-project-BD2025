SELECT
  o.olympics_id,
  o.name AS games_name,
  o.year,
  o.season,
  o.city,
  COUNT(pi.athlete_id) AS medalists
FROM OLYMPICS o
JOIN EVENT e ON e.olympics_id = o.olympics_id
JOIN PARTICIPATED_IN pi ON pi.event_id = e.event_id
GROUP BY o.olympics_id, o.name, o.year, o.season, o.city
ORDER BY medalists DESC, o.year
LIMIT 10;
