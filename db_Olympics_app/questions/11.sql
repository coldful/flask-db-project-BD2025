SELECT
  s.name AS sport,
  ROUND(AVG(pi.age), 2) AS avg_age,
  COUNT(*) AS medalists_with_age
FROM PARTICIPATED_IN pi
JOIN EVENT e ON e.event_id = pi.event_id
JOIN SPORT s ON s.sport_id = e.sport_id
WHERE pi.age IS NOT NULL
GROUP BY s.name
HAVING medalists_with_age > 0
ORDER BY avg_age ASC, sport;
