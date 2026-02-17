-- SQL Server Queries
CREATE TABLE
    detalle_cn (
        management_id INT NOT NULL, -- Codigo de Gerencia
        management_name NVARCHAR (30) NOT NULL, -- Nombre de Gerencia
        sector_id INT NOT NULL, -- Codigo de Sector
        sector_name NVARCHAR (30) NOT NULL, -- Nombre de Sector
        group_id INT NOT NULL, -- Codigo de Grupo
        leader NVARCHAR (100) NOT NULL, -- Codigo de Lider
        color NVARCHAR (10) NOT NULL, -- Nivel de Color (no obligatorio)
        cn_code INT NOT NULL, -- Codigo de CN
        cn_name NVARCHAR (100) NOT NULL, -- Nombre de CN
        month TINYINT NOT NULL, -- Mes
        year SMALLINT NOT NULL, -- Año
        p_digital INT NULL, -- Indicador Digital (1 o 0) (PEDIDOS DIGITALES)
        ingreso_mn INT NULL, -- Indicador Ingresos a Mi Negocio (1 o 0) (Ingresos a Mi Negocio) 
        mixed INT NULL, -- Indicador Consultora Mixta (1 o 0) (Tienda online Activas)
        impersonation INT NULL, -- Indicador de Impersonacion (1 o 0) (Pedido Autónomo)
        magazine INT NULL, -- Indicador de Revista (1 o 0) (Comparte Revista digital)
        origen NVARCHAR (10) NULL, -- Si es de Avon o Natura (no obligatorio)
        status INT NOT NULL, -- Estado de la Informacion
        INDEX cn_code_index (cn_code),
        INDEX year_index (year),
        INDEX month_index (month)
    );

-- detalle_grupo 
SELECT
    oi.sales_management_code AS management_id,
    oi.sales_management_name AS management_name,
    oi.sector_code AS sector_id,
    oi.sector_name AS sector_name,
    oi.group_code AS group_id,
    cci.leader_code AS leader,
    UPPER(oi.level_name) AS color,
    YEAR (DATE (oi.order_date)) AS year,
    MONTH (DATE (oi.order_date)) AS month,
    SUM(
        CASE
            WHEN chk.OrderId > 0 THEN 1
            ELSE 0
        END
    ) AS p_digital,
    SUM(
        CASE
            WHEN mn.cnCode IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS ingreso_mn,
    SUM(
        CASE
            WHEN c.person_number IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS mixed,
    SUM(
        CASE
            WHEN oi.flag_imp > 0 THEN 1
            ELSE 0
        END
    ) AS impersonation,
    SUM(
        CASE
            WHEN mg.cnId IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS magazine
FROM
    product.elo_modelo_combinado.commercial_orders_index oi
    LEFT JOIN platform.gdp_gpp_cadwf_people_replica.document doc ON oi.person_id = doc.person_id
    LEFT JOIN product.elo_modelo_combinado.commercial_consultant_index cci ON oi.person_code = cci.person_code
    LEFT JOIN platform.commerce_cloud_natura_chile_replica.consultants c ON LOWER(c.document) = LOWER(doc.number)
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.checkout chk ON oi.person_code = chk.cnId
    AND DATE (oi.order_date) = DATE (chk.created_at)
    LEFT JOIN platform.google_analytics_3_raw.vw_acessos_total mn ON oi.person_code = mn.cnCode
    AND DATE (oi.order_date) = mn.data
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.user_action mg ON oi.person_code = mg.cnId
    AND DATE (oi.order_date) = DATE (mg.created_at)
WHERE
    oi.country_code = 152
    AND cci.country_code = 152
    AND YEAR (DATE (oi.order_date)) >= 2024
    AND cci.operational_cycle >= 202401
    AND doc.number IS NOT NULL
    AND chk.country = 'CL'
    AND chk.cnId > 0
    AND mn.country = 'CL'
GROUP BY
    oi.sales_management_code,
    oi.sales_management_name,
    oi.sector_code,
    oi.sector_name,
    oi.group_code,
    cci.leader_code,
    UPPER(oi.level_name) AS color,
    YEAR (DATE (oi.order_date)),
    MONTH (DATE (oi.order_date));

--detalle_sector (
SELECT
    oi.sales_management_code AS management_id,
    oi.sales_management_name AS management_name,
    oi.sector_code AS sector_id,
    oi.sector_name AS sector_name,
    YEAR (DATE (oi.order_date)) AS year,
    MONTH (DATE (oi.order_date)) AS month,
    SUM(
        CASE
            WHEN chk.OrderId > 0 THEN 1
            ELSE 0
        END
    ) AS p_digital,
    SUM(
        CASE
            WHEN mn.cnCode IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS ingreso_mn,
    SUM(
        CASE
            WHEN c.person_number IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS mixed,
    SUM(
        CASE
            WHEN oi.flag_imp > 0 THEN 1
            ELSE 0
        END
    ) AS impersonation,
    SUM(
        CASE
            WHEN mg.cnId IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS magazine
FROM
    product.elo_modelo_combinado.commercial_orders_index oi
    LEFT JOIN platform.gdp_gpp_cadwf_people_replica.document doc ON oi.person_id = doc.person_id
    LEFT JOIN product.elo_modelo_combinado.commercial_consultant_index cci ON oi.person_code = cci.person_code
    LEFT JOIN platform.commerce_cloud_natura_chile_replica.consultants c ON LOWER(c.document) = LOWER(doc.number)
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.checkout chk ON oi.person_code = chk.cnId
    AND DATE (oi.order_date) = DATE (chk.created_at)
    LEFT JOIN platform.google_analytics_3_raw.vw_acessos_total mn ON oi.person_code = mn.cnCode
    AND DATE (oi.order_date) = mn.data
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.user_action mg ON oi.person_code = mg.cnId
    AND DATE (oi.order_date) = DATE (mg.created_at)
WHERE
    oi.country_code = 152
    AND cci.country_code = 152
    AND YEAR (DATE (oi.order_date)) >= 2024
    AND cci.operational_cycle >= 202401
    AND doc.number IS NOT NULL
    AND chk.country = 'CL'
    AND chk.cnId > 0
    AND mn.country = 'CL'
GROUP BY
    oi.sales_management_code,
    oi.sales_management_name,
    oi.sector_code,
    oi.sector_name,
    YEAR (DATE (oi.order_date)),
    MONTH (DATE (oi.order_date));

--detalle_gerencia 
SELECT
    oi.sales_management_code AS management_id,
    oi.sales_management_name AS management_name,
    YEAR (DATE (oi.order_date)) AS year,
    MONTH (DATE (oi.order_date)) AS month,
    SUM(
        CASE
            WHEN chk.OrderId > 0 THEN 1
            ELSE 0
        END
    ) AS p_digital,
    SUM(
        CASE
            WHEN mn.cnCode IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS ingreso_mn,
    SUM(
        CASE
            WHEN c.person_number IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS mixed,
    SUM(
        CASE
            WHEN oi.flag_imp > 0 THEN 1
            ELSE 0
        END
    ) AS impersonation,
    SUM(
        CASE
            WHEN mg.cnId IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS magazine
FROM
    product.elo_modelo_combinado.commercial_orders_index oi
    LEFT JOIN platform.gdp_gpp_cadwf_people_replica.document doc ON oi.person_id = doc.person_id
    LEFT JOIN product.elo_modelo_combinado.commercial_consultant_index cci ON oi.person_code = cci.person_code
    LEFT JOIN platform.commerce_cloud_natura_chile_replica.consultants c ON LOWER(c.document) = LOWER(doc.number)
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.checkout chk ON oi.person_code = chk.cnId
    AND DATE (oi.order_date) = DATE (chk.created_at)
    LEFT JOIN platform.google_analytics_3_raw.vw_acessos_total mn ON oi.person_code = mn.cnCode
    AND DATE (oi.order_date) = mn.data
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.user_action mg ON oi.person_code = mg.cnId
    AND DATE (oi.order_date) = DATE (mg.created_at)
WHERE
    oi.country_code = 152
    AND cci.country_code = 152
    AND YEAR (DATE (oi.order_date)) >= 2024
    AND cci.operational_cycle >= 202401
    AND doc.number IS NOT NULL
    AND chk.country = 'CL'
    AND chk.cnId > 0
    AND mn.country = 'CL'
GROUP BY
    oi.sales_management_code,
    oi.sales_management_name,
    YEAR (DATE (oi.order_date)),
    MONTH (DATE (oi.order_date));

--detalle_pais 
SELECT
    oi.country,
    YEAR (DATE (oi.order_date)) AS year,
    MONTH (DATE (oi.order_date)) AS month,
    SUM(
        CASE
            WHEN chk.OrderId > 0 THEN 1
            ELSE 0
        END
    ) AS p_digital,
    SUM(
        CASE
            WHEN mn.cnCode IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS ingreso_mn,
    SUM(
        CASE
            WHEN c.person_number IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS mixed,
    SUM(
        CASE
            WHEN oi.flag_imp > 0 THEN 1
            ELSE 0
        END
    ) AS impersonation,
    SUM(
        CASE
            WHEN mg.cnId IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS magazine
FROM
    product.elo_modelo_combinado.commercial_orders_index oi
    LEFT JOIN platform.gdp_gpp_cadwf_people_replica.document doc ON oi.person_id = doc.person_id
    LEFT JOIN product.elo_modelo_combinado.commercial_consultant_index cci ON oi.person_code = cci.person_code
    LEFT JOIN platform.commerce_cloud_natura_chile_replica.consultants c ON LOWER(c.document) = LOWER(doc.number)
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.checkout chk ON oi.person_code = chk.cnId
    AND DATE (oi.order_date) = DATE (chk.created_at)
    LEFT JOIN platform.google_analytics_3_raw.vw_acessos_total mn ON oi.person_code = mn.cnCode
    AND DATE (oi.order_date) = mn.data
    LEFT JOIN platform.transactional_data_intencao_transactional_data_prd_app_replica.user_action mg ON oi.person_code = mg.cnId
    AND DATE (oi.order_date) = DATE (mg.created_at)
WHERE
    oi.country_code = 152
    AND cci.country_code = 152
    AND YEAR (DATE (oi.order_date)) >= 2024
    AND cci.operational_cycle >= 202401
    AND doc.number IS NOT NULL
    AND chk.country = 'CL'
    AND chk.cnId > 0
    AND mn.country = 'CL'
GROUP BY
    oi.country,
    YEAR (DATE (oi.order_date)),
    MONTH (DATE (oi.order_date));