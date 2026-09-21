-- Yönetim raporunun tek komutla üretilen hali.
-- Raporun ana tablosu: bir yılın bir kaynağındaki kalemler, plana göre sapmaları
-- ve (yıl bitmemişse) yıl sonu tahminleriyle birlikte, sapması en büyükten sıralı.
--
-- Kullanım:
--   EXEC sp_monthly_report @year = 2026, @source = 'balance';
--   EXEC sp_monthly_report @year = 2025, @source = 'ministries', @top = 10;
CREATE OR ALTER PROCEDURE sp_monthly_report
    @year   SMALLINT,
    @source VARCHAR(20) = 'balance',
    @top    INT         = 1000
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@top)
        a.main_item,
        a.item,
        a.months_reported,
        CAST(a.actual   / 1000000 AS DECIMAL(12, 1)) AS actual_bn_try,
        CAST(a.planned     / 1000000 AS DECIMAL(12, 1)) AS plan_bn_try,
        CAST(a.variance / 1000000 AS DECIMAL(12, 1)) AS variance_bn_try,
        CAST(a.pct_of_plan            AS DECIMAL(6, 1)) AS pct_of_plan,
        CAST(f.forecast_year_end / 1000000 AS DECIMAL(12, 1)) AS forecast_bn_try,
        CAST(f.forecast_pct_of_plan   AS DECIMAL(6, 1)) AS forecast_pct_of_plan
    FROM v_annual a
    LEFT JOIN v_year_end_forecast f
        ON f.source = a.source AND f.year = a.year AND f.item = a.item
    WHERE a.year = @year AND a.source = @source
    ORDER BY ABS(a.variance) DESC;
END;
GO
