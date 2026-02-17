WITH aggregated_delta AS (
    SELECT
        management_id,
        management_name,
        year,
        month,
        CAST(SUM(CASE WHEN p_digital = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS p_digital,
        CAST(SUM(CASE WHEN ingreso_mn = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS ingreso_mn,
        CAST(SUM(CASE WHEN mixed = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS mixed,
        CAST(SUM(CASE WHEN impersonation = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS impersonation,
        CAST(SUM(CASE WHEN magazine = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS magazine,
        GETDATE() AS FechaIngesta,
        0 AS status
    FROM [panel_digital].[detalle_cn]
    WHERE year >= 2024
    GROUP BY management_id, management_name, year, month
)

MERGE [panel_digital].[detalle_gerencia] AS target
USING aggregated_delta AS source
    ON ISNULL(target.management_id, -1) = ISNULL(source.management_id, -1)
    AND ISNULL(target.management_name, '') = ISNULL(source.management_name, '')
    AND target.year = source.year
    AND target.month = source.month

WHEN MATCHED THEN
    UPDATE SET
        target.p_digital = source.p_digital,
        target.ingreso_mn = source.ingreso_mn,
        target.mixed = source.mixed,
        target.impersonation = source.impersonation,
        target.magazine = source.magazine,
        target.status = source.status,
        target.FechaIngesta = source.FechaIngesta

WHEN NOT MATCHED THEN
    INSERT (
        management_id, management_name,
        month, year,
        p_digital, ingreso_mn, mixed,
        impersonation, magazine,
        status, FechaIngesta
    )
    VALUES (
        source.management_id, source.management_name,
        source.month, source.year,
        source.p_digital, source.ingreso_mn, source.mixed,
        source.impersonation, source.magazine,
        source.status, source.FechaIngesta
    );

