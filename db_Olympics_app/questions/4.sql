SELECT
  sex,
  ROUND(AVG(height), 2) AS avg_height,
  ROUND(AVG(weight), 2) AS avg_weight,
  COUNT(*) AS athletes
FROM ATHLETE
GROUP BY sex;
