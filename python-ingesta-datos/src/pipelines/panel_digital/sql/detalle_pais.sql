SELECT
    origen AS country,
    year,
    month,
    SUM(CASE WHEN p_digital = 1 THEN 1 ELSE 0 END) AS p_digital,
    SUM(CASE WHEN ingreso_mn = 1 THEN 1 ELSE 0 END) AS ingreso_mn,
    SUM(CASE WHEN mixed = 1 THEN 1 ELSE 0 END) AS mixed,
    SUM(CASE WHEN impersonation = 1 THEN 1 ELSE 0 END) AS impersonation,
    SUM(CASE WHEN magazine = 1 THEN 1 ELSE 0 END) AS magazine
FROM detalle_cn
WHERE year >= 2024
GROUP BY origen, year, month
ORDER BY year, month;
