-- Raporun beslendiği görünümler. apply_sql.py bu dosyayı veritabanına uygular.
-- Tutarlar bin TL.
--
-- Yüzdeler iki koşulda hesaplanmaz, çünkü anlamsız çıkar:
--   * planı sıfır ya da eksi olan kalemler,
--   * denge satırları (bütçe dengesi, faiz dışı denge). Bunlar gelir eksi gider
--     olarak hesaplandığı için planları sıfıra yakındır; küçük bir sapma bile
--     yüzdeyi binlere çıkarır. Denge satırlarında tutar farkına bakılır.

-- 1) Aylık gidiş: her kalemin her ayı, yılbaşından o aya kümülatifiyle birlikte.
-- Son sütun kıyas içindir: geçmiş yıllarda aynı ayda planın yüzde kaçı
-- gerçekleşmişti? Yıl bitmeden "%64 az mı çok mu" sorusu ancak buna bakarak
-- cevaplanabilir. Kıyas yalnızca 12 ayı yayımlanmış yıllardan hesaplanır.
CREATE OR ALTER VIEW v_monthly AS
WITH base AS (
    SELECT
        a.source, a.year, a.month, a.main_item, a.item,
        a.amount_thousand_try AS actual,
        SUM(a.amount_thousand_try) OVER (
            PARTITION BY a.source, a.year, a.item
            ORDER BY a.month
            ROWS UNBOUNDED PRECEDING
        ) AS cumulative_actual,
        p.amount_thousand_try AS planned
    FROM actuals a
    LEFT JOIN plans p
        ON p.source = a.source AND p.year = a.year AND p.item = a.item
),
complete_years AS (
    SELECT source, year, item
    FROM base
    GROUP BY source, year, item
    HAVING COUNT(*) = 12
),
typical AS (
    SELECT b.source, b.item, b.month,
           AVG(100.0 * b.cumulative_actual / b.planned) AS typical_pct_of_plan
    FROM base b
    JOIN complete_years c
        ON c.source = b.source AND c.year = b.year AND c.item = b.item
    WHERE b.planned > 0 AND b.main_item <> 'Denge'
    GROUP BY b.source, b.item, b.month
)
SELECT
    b.source,
    b.year,
    b.month,
    b.main_item,
    b.item,
    b.actual,
    b.cumulative_actual,
    b.planned,
    CASE WHEN b.planned > 0 AND b.main_item <> 'Denge'
         THEN 100.0 * b.cumulative_actual / b.planned END AS cumulative_pct_of_plan,
    t.typical_pct_of_plan
FROM base b
LEFT JOIN typical t
    ON t.source = b.source AND t.item = b.item AND t.month = b.month;
GO

-- 2) Yıl özeti: yılın toplamı, planı ve sapması.
-- Yayımlanan ay sayısı da veriliyor; 12'den azsa yıl henüz bitmemiştir ve
-- sapma yorumlanırken bu dikkate alınmalıdır.
CREATE OR ALTER VIEW v_annual AS
SELECT
    a.source,
    a.year,
    a.main_item,
    a.item,
    COUNT(*)                          AS months_reported,
    CAST(CASE WHEN COUNT(*) = 12 THEN 1 ELSE 0 END AS BIT) AS is_complete_year,
    SUM(a.amount_thousand_try)        AS actual,
    MAX(p.amount_thousand_try)        AS planned,
    SUM(a.amount_thousand_try) - MAX(p.amount_thousand_try) AS variance,
    CASE WHEN MAX(p.amount_thousand_try) > 0 AND a.main_item <> 'Denge'
         THEN 100.0 * SUM(a.amount_thousand_try) / MAX(p.amount_thousand_try)
    END                               AS pct_of_plan
FROM actuals a
LEFT JOIN plans p
    ON p.source = a.source AND p.year = a.year AND p.item = a.item
GROUP BY a.source, a.year, a.main_item, a.item;
GO

-- 3) Sapma sıralaması: bir yıl içinde planından en çok ayrılan kalemler.
-- İki sıralama birden veriliyor: tutar olarak en büyük sapma (büyük kalemler öne
-- çıkar) ve yüzde olarak en büyük sapma (küçük ama oransal olarak çarpıcı kalemler).
CREATE OR ALTER VIEW v_variance_rank AS
SELECT
    source, year, main_item, item, months_reported, is_complete_year,
    actual, planned, variance, pct_of_plan,
    ROW_NUMBER() OVER (PARTITION BY source, year ORDER BY ABS(variance) DESC) AS rank_by_amount,
    ROW_NUMBER() OVER (PARTITION BY source, year ORDER BY ABS(pct_of_plan - 100) DESC) AS rank_by_pct
FROM v_annual
WHERE planned > 0 AND pct_of_plan IS NOT NULL;
GO

-- 4) Yıl sonu tahmini: henüz bitmemiş yıl için.
-- Yöntem: geçmiş yıllarda bu kalemin, yılın aynı ayına kadar yıllık toplamının
-- yüzde kaçı harcanmıştı? Bu ortalama pay, bu yılın kümülatifine uygulanır.
-- Makine öğrenmesi yok; finans ekiplerinin kullandığı "rolling forecast" mantığı.
-- Harcamaların yıl sonuna yığılması (Aralık'ta patlama) bu sayede hesaba katılır.
CREATE OR ALTER VIEW v_year_end_forecast AS
WITH complete_years AS (           -- yalnızca 12 ayı da yayımlanmış yıllar
    SELECT source, year, item
    FROM v_annual
    WHERE is_complete_year = 1 AND actual > 0
),
month_share AS (                   -- geçmiş yıllarda ayın yıl toplamındaki payı
    SELECT m.source, m.item, m.month,
           AVG(m.cumulative_actual / NULLIF(y.actual, 0)) AS share_of_year
    FROM v_monthly m
    JOIN complete_years c ON c.source = m.source AND c.year = m.year AND c.item = m.item
    JOIN v_annual y       ON y.source = m.source AND y.year = m.year AND y.item = m.item
    GROUP BY m.source, m.item, m.month
),
open_years AS (                    -- bitmemiş yıl ve son yayımlanan ayın kümülatifi
    SELECT a.source, a.year, a.main_item, a.item, a.months_reported, a.planned,
           m.cumulative_actual
    FROM v_annual a
    JOIN v_monthly m
        ON m.source = a.source AND m.year = a.year AND m.item = a.item
       AND m.month = a.months_reported
    WHERE a.is_complete_year = 0
)
SELECT
    o.source, o.year, o.main_item, o.item,
    o.months_reported,
    o.cumulative_actual,
    o.planned,
    s.share_of_year,
    CASE WHEN s.share_of_year > 0 THEN o.cumulative_actual / s.share_of_year END AS forecast_year_end,
    CASE WHEN s.share_of_year > 0 AND o.planned > 0
         THEN 100.0 * (o.cumulative_actual / s.share_of_year) / o.planned
    END AS forecast_pct_of_plan
FROM open_years o
LEFT JOIN month_share s
    ON s.source = o.source AND s.item = o.item AND s.month = o.months_reported;
GO

-- 5) Tahmin yönteminin geriye dönük testi.
-- Bitmiş her yıl için soru şu: elimizde yalnızca ilk N ay olsaydı, yıl sonunu ne
-- tahmin ederdik ve gerçekte ne oldu? Payı hesaplarken o yılın kendisi dışarıda
-- bırakılıyor, yoksa cevabı bilerek tahmin etmiş oluruz.
CREATE OR ALTER VIEW v_forecast_backtest AS
WITH complete_years AS (
    SELECT source, year, item, actual AS year_total
    FROM v_annual
    WHERE is_complete_year = 1 AND actual > 0
),
shares AS (
    SELECT m.source, m.year, m.item, m.month, m.cumulative_actual,
           c.year_total,
           m.cumulative_actual / c.year_total AS share_of_year
    FROM v_monthly m
    JOIN complete_years c
        ON c.source = m.source AND c.year = m.year AND c.item = m.item
)
SELECT
    s.source, s.year, s.item, s.month,
    s.cumulative_actual,
    s.year_total,
    o.share_of_other_years,
    CASE WHEN o.share_of_other_years > 0
         THEN s.cumulative_actual / o.share_of_other_years END AS forecast_year_end,
    CASE WHEN o.share_of_other_years > 0
         THEN 100.0 * ABS(s.cumulative_actual / o.share_of_other_years - s.year_total) / s.year_total
    END AS error_pct
FROM shares s
CROSS APPLY (
    SELECT AVG(other.share_of_year) AS share_of_other_years
    FROM shares other
    WHERE other.source = s.source AND other.item = s.item
      AND other.month = s.month AND other.year <> s.year
) o;
GO
