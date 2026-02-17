-- Eliminamos datos residuales de gerencia 2768 que dejó de existir en marzo 2025
--DELETE
--FROM [TDChile].[panel_digital].[detalle_cn]
--WHERE ([year] > 2025 OR [month] > 2) AND [management_id] = 200002768;

--GO

-- Llenamos tablas agrupadoras
TRUNCATE TABLE [panel_digital].[detalle_grupo];

INSERT
[panel_digital].[detalle_grupo] ([management_id]
      ,[management_name]
      ,[sector_id]
      ,[sector_name]
      ,[group_id]
      ,[leader]
      ,[color]
      ,[month]
      ,[year]
      ,[p_digital]
      ,[ingreso_mn]
      ,[mixed]
      ,[impersonation]
      ,[magazine]
	  ,[activa]
	,[total])

SELECT [management_id]
        , [management_name]
        , [sector_id]
        , [sector_name]
        , [group_id]
        , [leader]
        , '-' -- [color]
        , [month]
        , [year]
        , SUM ([p_digital]) AS p_digital
        , SUM ([ingreso_mn]) AS ingreso_mn
        , SUM ([mixed]) AS "mixed"
        , SUM ([impersonation]) AS impersonation
        , SUM ([magazine]) AS magazine
        , SUM (CASE WHEN [activa] = 1 THEN 1 ELSE 0 END) AS activa
        , COUNT ([id]) as total
FROM [TDChile].[panel_digital].[detalle_cn]
GROUP BY [management_id]
        , [management_name]
        , [sector_id]
        , [sector_name]
        , [group_id]
        , [leader]
    --,[color]
        , [month]
        , [year];

GO

TRUNCATE TABLE [panel_digital].[detalle_sector];

INSERT
[panel_digital].[detalle_sector] ([management_id]
      ,[management_name]
      ,[sector_id]
      ,[sector_name]
      ,[month]
      ,[year]
      ,[p_digital]
      ,[ingreso_mn]
      ,[mixed]
      ,[impersonation]
      ,[magazine]
	  ,[activa]
	,[total])

SELECT [management_id]
        , MAX ([management_name])
        , [sector_id]
        , MAX ([sector_name])
        , [month]
        , [year]
        , SUM ([p_digital]) AS p_digital
        , SUM ([ingreso_mn]) AS ingreso_mn
        , SUM ([mixed]) AS "mixed"
        , SUM ([impersonation]) AS impersonation
        , SUM ([magazine]) AS magazine
        , SUM (CASE WHEN [activa] = 1 THEN 1 ELSE 0 END) AS activa
        , COUNT ([id]) as total
FROM [TDChile].[panel_digital].[detalle_cn]
GROUP BY [management_id]
    --,[management_name]
        , [sector_id]
    --,[sector_name]
        , [month]
        , [year];

GO

TRUNCATE TABLE [panel_digital].[detalle_gerencia];

INSERT
[panel_digital].[detalle_gerencia] ([management_id]
      ,[management_name]
      ,[month]
      ,[year]
      ,[p_digital]
      ,[ingreso_mn]
      ,[mixed]
      ,[impersonation]
      ,[magazine]
	  ,[activa]
	,[total])

SELECT [management_id]
        , MAX ([management_name])
        , [month]
        , [year]
        , SUM ([p_digital]) AS p_digital
        , SUM ([ingreso_mn]) AS ingreso_mn
        , SUM ([mixed]) AS "mixed"
        , SUM ([impersonation]) AS impersonation
        , SUM ([magazine]) AS magazine
        , SUM (CASE WHEN [activa] = 1 THEN 1 ELSE 0 END) AS activa
        , COUNT ([id]) as total
FROM [TDChile].[panel_digital].[detalle_cn]
GROUP BY [management_id]
    --,[management_name]
        , [month]
        , [year];

GO

TRUNCATE TABLE [panel_digital].[detalle_pais];

INSERT
[panel_digital].[detalle_pais] ([month]
      ,[year]
      ,[p_digital]
      ,[ingreso_mn]
      ,[mixed]
      ,[impersonation]
      ,[magazine]
	  ,[activa]
	,[total])

SELECT [month]
        , [year]
        , SUM ([p_digital]) AS p_digital
        , SUM ([ingreso_mn]) AS ingreso_mn
        , SUM ([mixed]) AS "mixed"
        , SUM ([impersonation]) AS impersonation
        , SUM ([magazine]) AS magazine
        , SUM (CASE WHEN [activa] = 1 THEN 1 ELSE 0 END) AS activa
        , COUNT ([id]) as total
FROM [TDChile].[panel_digital].[detalle_cn]
GROUP BY [month]
        , [year];

GO