SELECT
  city,
  COUNT(*) AS editions
FROM OLYMPICS
GROUP BY city
ORDER BY editions DESC, city;
