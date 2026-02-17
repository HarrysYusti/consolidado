WITH aggregated_delta AS (
    SELECT
        management_id,
        management_name,
        sector_id,
        sector_name,
        group_id,
        leader,
        color,
        year,
        month,
        CAST(SUM(CASE WHEN p_digital = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS p_digital,
        CAST(SUM(CASE WHEN ingreso_mn = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS ingreso_mn,
        CAST(SUM(CASE WHEN mixed = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS mixed,
        CAST(SUM(CASE WHEN impersonation = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS impersonation,
        CAST(SUM(CASE WHEN magazine = 1 THEN 1 ELSE 0 END) AS DECIMAL(30,4)) AS magazine,
        GETDATE() AS FechaIngesta,
        1 AS status
    FROM [panel_digital].detalle_cn
    WHERE year >= 2024 and group_id is not null
    GROUP BY
        management_id, management_name,
        sector_id, sector_name,
        group_id, leader, color,
        year, month
)

MERGE [panel_digital].[detalle_grupo] AS target
USING aggregated_delta AS source
    ON
        ISNULL(target.management_id, -1) = ISNULL(source.management_id, -1) AND
        ISNULL(target.management_name, '') = ISNULL(source.management_name, '') AND
        ISNULL(target.sector_id, -1) = ISNULL(source.sector_id, -1) AND
        ISNULL(target.sector_name, '') = ISNULL(source.sector_name, '') AND
        ISNULL(target.group_id, -1) = ISNULL(source.group_id, -1) AND
        ISNULL(target.leader, '') = ISNULL(source.leader, '') AND
        ISNULL(target.color, '') = ISNULL(source.color, '') AND
        target.year = source.year AND
        target.month = source.month

-- UPDATE si ya existe
WHEN MATCHED THEN
    UPDATE SET
        target.p_digital = source.p_digital,
        target.ingreso_mn = source.ingreso_mn,
        target.mixed = source.mixed,
        target.impersonation = source.impersonation,
        target.magazine = source.magazine,
        target.status = source.status,
        target.FechaIngesta = source.FechaIngesta

-- INSERT si no existe
WHEN NOT MATCHED THEN
    INSERT (
        management_id, management_name,
        sector_id, sector_name,
        group_id, leader, color,
        month, year,
        p_digital, ingreso_mn, mixed,
        impersonation, magazine,
        status, FechaIngesta
    )
    VALUES (
        source.management_id, source.management_name,
        source.sector_id, source.sector_name,
        source.group_id, source.leader, source.color,
        source.month, source.year,
        source.p_digital, source.ingreso_mn, source.mixed,
        source.impersonation, source.magazine,
        source.status, source.FechaIngesta
    );