-- Power BI'ın filtre tabloları (dimension).
-- Rapor sayfasındaki yıl ve kalem filtreleri bunlara bağlanır; hesap
-- görünümleri de buradan filtrelenir. Böylece tek bir filtre bütün görselleri
-- aynı anda etkiler. Veri ambarı dilinde buna yıldız şema deniyor: ortada
-- ölçümler, kenarlarda filtre tabloları.

-- Yıl listesi
CREATE OR ALTER VIEW dim_year AS
SELECT DISTINCT year FROM actuals;
GO

-- Kalem ve kurum listesi.
-- item_key, kaynağı ve adı birleştiren anahtar: aynı ad birden fazla kaynakta
-- geçebildiği için ("Memurlar" gider detayında, kurum adları kurumsal tabloda)
-- tek başına ad anahtar olamaz.
--
-- is_total: bu satır bir toplam mı, yoksa alt kalem mi? Tablolarda ikisi yan yana
-- duruyor: "Harcamalar" satırı personeli, faizi ve yatırımı zaten içeriyor.
-- Grafiklerde ve sıralamalarda alt kalemler kullanılır (is_total = 0), yoksa
-- aynı para iki kez sayılır. Kutularda ise toplam satırı kullanılır.
CREATE OR ALTER VIEW dim_item AS
SELECT
    source + '|' + item AS item_key,
    source,
    MIN(main_item)      AS main_item,
    item,
    -- Raporda gösterilecek ad. Kaynak dosyadaki hiyerarşi işaretleri ("1.", "a)",
    -- "-", "1-") ayıklanıyor. Ham ad anahtar olarak kaldığı için eşleşmeler bozulmuyor.
    LTRIM(CASE
        WHEN item LIKE '[0-9]. %'  THEN STUFF(item, 1, 3, '')
        WHEN item LIKE '[A-Z]. %'  THEN STUFF(item, 1, 3, '')
        WHEN item LIKE '[a-z]) %'  THEN STUFF(item, 1, 3, '')
        WHEN item LIKE '[0-9]-%'   THEN STUFF(item, 1, 2, '')
        WHEN item LIKE '-%'        THEN STUFF(item, 1, 1, '')
        ELSE item
    END)                AS display_name,
    CAST(CASE
        WHEN source = 'balance' AND item IN (
            N'Harcamalar', N'1-Faiz Hariç Harcama', N'Gelirler',
            N'1-Genel Bütçe Gelirleri', N'Bütçe Dengesi', N'Faiz Dışı Denge') THEN 1
        WHEN source = 'expense_detail' AND item = MIN(main_item) THEN 1
        ELSE 0
    END AS BIT) AS is_total
FROM actuals
GROUP BY source, item;
GO
