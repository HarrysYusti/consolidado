WITH orders_base AS (
  SELECT *
  FROM product.elo_modelo_combinado.commercial_orders_index
  WHERE 
    country_code = 152
    AND DATE(order_date) >= '2024-01-01'
),

consultants_index AS (
  SELECT person_code, operational_cycle, country_code
  FROM product.elo_modelo_combinado.commercial_consultant_index
  WHERE 
    country_code = 152
    AND operational_cycle >= 202401
),

documents AS (
  SELECT person_id, number
  FROM platform.gdp_gpp_cadwf_people_replica.document
  WHERE number IS NOT NULL
),

business_relation_filtered AS (
  SELECT structure_code, person_code
  FROM platform.gdp_gpp_brm_brm_replica.business_relation
  WHERE 
    function = 4
    AND country = 152
    AND structure_level = 3
),

commerce_consultants AS (
  SELECT document, person_number
  FROM platform.commerce_cloud_natura_chile_replica.consultants
),

checkout_filtered AS (
  SELECT cnId, created_at
  FROM platform.transactional_data_intencao_transactional_data_prd_app_replica.checkout
  WHERE 
    country = 'CL'
    AND cnId > 0
),
cadastro AS (
    SELECT DISTINCT
        person_code AS consultora,
        country,
        mes
    FROM product.indicadores_ss.cadastro_indicadores_mensal
    WHERE mes >= '202401'
),

-- 2. Accesos a Mi Negocio (marzo a julio)
acessos_mn AS (
    SELECT DISTINCT
        cnCode AS consultora,
        Country AS pais
    FROM platform.google_analytics_3_raw.vw_acessos_total
    WHERE year(data) >=2024
),

-- 3. Unión de ambas fuentes (consultoras que accedieron a MN y están en el padrón)
cadastro_acessos AS (
    SELECT
        c.consultora AS consultora_cadastro,
        a.consultora AS consultora_acceso,
        c.mes,
        c.country AS pais
    FROM cadastro c
    LEFT JOIN acessos_mn a
      ON c.consultora = a.consultora
      AND c.country = a.pais
),
magazine_filtered AS (
  SELECT cnId, created_at
  FROM platform.transactional_data_intencao_transactional_data_prd_app_replica.user_action
  where eventName in ('RI_NATURA_SPACE_SHARE_WITHOUT_DS', 'RI_NATURA_SPACE_SHARE_WITH_DS')
  and country ='CL'
)

SELECT 
  oi.sales_management_code AS management_id,
  oi.sales_management_name AS management_name,
  oi.sector_code AS sector_id,
  oi.sector_name AS sector_name,
  oi.group_code AS group_id,
  br.person_code AS leader_code,
  UPPER(oi.level_name) AS color,
  oi.person_code AS cn_code,
  UPPER(oi.person_name) AS cn_name,
  YEAR(DATE(oi.order_date)) AS year,
  MONTH(DATE(oi.order_date)) AS month,
  IF(chk.cnId IS NOT NULL, 1, 0) AS p_digital,
  IF(mn.consultora_acceso IS NOT NULL, 1, 0) AS ingreso_mn,
  IF(c.person_number IS NOT NULL, 1, 0) AS mixed,
  IF(oi.flag_imp > 0, 1, 0) AS impersonation,
  IF(mg.cnId IS NOT NULL, 1, 0) AS magazine

FROM orders_base oi
--####-
LEFT JOIN documents doc
  ON oi.person_id = doc.person_id
--####-
LEFT JOIN business_relation_filtered br
  ON oi.group_code = br.structure_code
--####-
LEFT JOIN consultants_index cci
  ON oi.person_code = cci.person_code
  AND oi.order_cycle = cci.operational_cycle
--####-
LEFT JOIN commerce_consultants c
  ON LOWER(c.document) = LOWER(doc.number)
--####-
LEFT JOIN checkout_filtered chk
  ON chk.cnId = oi.person_code AND DATE(chk.created_at) = DATE(oi.order_date)
--####-
LEFT JOIN cadastro_acessos mn
  ON oi.person_code = mn.consultora_cadastro
--####-
LEFT JOIN magazine_filtered mg
  ON mg.cnId = oi.person_code AND DATE(mg.created_at) = DATE(oi.order_date)

GROUP BY ALL
ORDER BY year, month