SELECT
  o.city,
  o.season,
  o.year,
  COUNT(e.event_id) AS event_count
FROM OLYMPICS o
JOIN EVENT e ON e.olympics_id = o.olympics_id
GROUP BY o.city, o.season, o.year
ORDER BY event_count DESC, o.year;
