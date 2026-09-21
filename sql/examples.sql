-- Örnek sorgular. VS Code'da bu dosyayı açıp istediğin sorgunun üzerine gelip
-- fareyle seçtikten sonra Ctrl+Shift+E ile çalıştırabilirsiniz.

-- 1) Bu yıl (2026) 8 ay sonunda ne durumda?
SELECT item,
       CAST(cumulative_actual / 1e6 AS DECIMAL(10,0)) AS gerceklesen_milyar,
       CAST(planned / 1e6          AS DECIMAL(10,0)) AS yillik_plan_milyar,
       CAST(cumulative_pct_of_plan AS DECIMAL(5,1))  AS yuzde
FROM v_monthly
WHERE source = 'balance' AND year = 2026 AND month = 8 AND main_item = 'Harcamalar'
ORDER BY cumulative_actual DESC;

-- 2) 2025'te planı en çok aşan 10 kalem (gider detayı)
SELECT TOP 10 item,
       CAST(actual / 1e6   AS DECIMAL(10,0)) AS gerceklesen_milyar,
       CAST(planned / 1e6  AS DECIMAL(10,0)) AS plan_milyar,
       CAST(pct_of_plan    AS DECIMAL(5,1))  AS yuzde
FROM v_variance_rank
WHERE source = 'expense_detail' AND year = 2025
ORDER BY rank_by_amount;

-- 3) 2025'te bütçesini aşan bakanlıklar
SELECT item AS kurum,
       CAST(actual / 1e6  AS DECIMAL(10,0)) AS harcanan_milyar,
       CAST(planned / 1e6 AS DECIMAL(10,0)) AS plan_milyar,
       CAST(pct_of_plan   AS DECIMAL(5,1))  AS yuzde
FROM v_annual
WHERE source = 'ministries' AND year = 2025 AND pct_of_plan > 100
ORDER BY pct_of_plan DESC;

-- 4) Bir kalemin yıllar içindeki ayrılan bütçeye uyma oranı
SELECT year, CAST(pct_of_plan AS DECIMAL(5,1)) AS yuzde, is_complete_year AS yil_tam_mi
FROM v_annual
WHERE source = 'balance' AND item = N'Sermaye Giderleri'
ORDER BY year;

-- 5) 2026 yıl sonu tahmini
SELECT item,
       CAST(cumulative_actual / 1e6   AS DECIMAL(10,0)) AS bugune_kadar_milyar,
       CAST(share_of_year * 100       AS DECIMAL(5,1))  AS gecmis_yillarda_bu_aya_kadar_yuzde,
       CAST(forecast_year_end / 1e6   AS DECIMAL(10,0)) AS yil_sonu_tahmini_milyar,
       CAST(forecast_pct_of_plan      AS DECIMAL(5,1))  AS plana_gore_yuzde
FROM v_year_end_forecast
WHERE source = 'balance' AND main_item = 'Harcamalar'
ORDER BY forecast_year_end DESC;

-- 6) Tahmin ne kadar isabetli? Geriye dönük testin ay bazında medyan hatası
SELECT DISTINCT month AS ay,
       CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY error_pct)
            OVER (PARTITION BY month) AS DECIMAL(5,1)) AS medyan_hata_yuzde
FROM v_forecast_backtest
WHERE source = 'balance'
ORDER BY ay;

-- 7) Yönetim raporu: yordamı çağır
EXEC sp_monthly_report @year = 2026, @source = 'balance';
EXEC sp_monthly_report @year = 2025, @source = 'ministries', @top = 10;
