[English](README.md) | **Türkçe**

# Hazine Nabzı

> Proje yapım aşamasında. Bu dosya her gün, o günün işiyle birlikte doldurulacak.

Türkiye merkezi yönetim bütçesinde yıl başında planlanan tutarlarla ay ay gerçekleşen tutarları karşılaştıran, otomatik çalışan raporlama projesi.

## Ne yapıyor

Bir finans ekibinin her ay yaptığı işi otomatikleştiriyor: planlanan bütçe ile gerçekleşen harcamayı karşılaştırıyor, sapmaları buluyor ve raporluyor.

Veri, Hazine ve Maliye Bakanlığı Muhasebat Genel Müdürlüğü'nün her ay yayımladığı bütçe tabloları. Proje bu tabloları kendisi indiriyor, temizliyor, veritabanına yüklüyor ve Power BI raporuna dönüştürüyor.

Cevapladığı sorular:

1. Hangi harcama ve gelir kalemleri plandan en çok sapıyor?
2. Hangi bakanlık bütçesini aştı, hangisi altında kaldı?
3. Sapma yılın hangi ayında ortaya çıkıyor?
4. Bu tablo yıldan yıla tekrar ediyor mu?
5. Yılın ilk aylarına bakarak yıl sonu tahmin edilebilir mi?

## Veri

**Kaynak:** [Muhasebat Genel Müdürlüğü, Merkezi Yönetim Bütçe İstatistikleri](https://muhasebat.hmb.gov.tr/merkezi-yonetim-butce-istatistikleri).

**Kapsam:** 2015–2026, aylık. 2026 yılı yayımlanan son aya (Agustos) kadar.

Her yıl için üç tablo kullanılıyor:

| Tablo | İçerik | Satır |
|---|---|---|
| Bütçe denge tablosu | Gelir ve giderin ana kalemleri, bütçe açığı | 23 kalem |
| Gider detay tablosu | Giderlerin alt kalemleri | 23 seçilmiş kalem ([`items.csv`](items.csv)) |
| Kurumsal tablo | Bakanlıklar ve diğer genel bütçeli kurumlar | 41–52 kurum |

Üç tabloda da her kalem için 12 ayın gerçekleşmesi ve yıl başındaki plan var. Plan, Meclis'in onayladığı Bütçe Kanunu'ndaki başlangıç ödeneği.

## Temizlik

36 ham Excel dosyası iki tabloya dönüştürüldü: `data/clean/actuals.csv` (aylık gerçekleşen, 13.728 satır) ve `data/clean/plans.csv` (yıllık plan, 1.174 satır).

Her satır tek bir ölçüm: bir kalemin, bir yıldaki ve o yıldaki spesifik bir aydaki tutarı.

| Sütun | İçerik |
|---|---|
| `source` | Satırın geldiği tablo: `balance`, `expense_detail`, `ministries` |
| `year`, `month` | Yıl ve ay (1–12). `plans.csv`'de ay yok, plan yıllık |
| `main_item` | Üst grup: Harcamalar / Gelirler / Denge, ana gider kalemi ya da Genel Bütçeli İdareler |
| `item` | Kalem ya da kurum adı |
| `amount_thousand_try` | Tutar, bin TL |

Tablolar yıldan yıla aynı formatta olmadığı için temizlikte çözülenler:

- **Sütunlar sırayla değil adıyla bulunuyor.** Bazı yıllarda fazladan sütun var, sıralar kayıyor. Plan sütununun adı 12 yılda yedi farklı şekilde yazılmıştı: "Bütçe Tahmini", "2022 Toplam Bütçe Tahmini*", "Bütçe Başlangıç Ödeneği *", "Toplam Bütçe Ödeneği*" gibi. Standart hale getirildi
- **Plan olarak başlangıç ödeneği alınıyor.** Kurumsal tabloda 2015–2024 arasında ikinci bir sütun daha var ("Ödenek Toplamı"): yıl içindeki aktarımlardan sonraki güncel ödenek. Diğer iki tabloda karşılığı olmadığı için kullanılmadı.
- **Ay adları bazı yıllarda kısaltılmış:** "Ocak" yerine "Oca", 2015'te Ağustos "Agu".
- **Kalem adları 2021'de değişmiş.** "KİT Görev Zararları" = "KİT Görevlendirme Giderleri" gibi yedi ad. Eski adlar [`items.csv`](items.csv) dosyasındaki `old_name` sütununda eşleştiriliyor.
- **Aynı ad tabloda birden çok kez geçebiliyor.** "Memurlar" hem personel hem sosyal güvenlik primi altında var; "Tahvil Faizi" iki yerde geçiyor ve biri boş. `items.csv`'deki `search_under` sütunu kalemin hangi başlığın altında aranacağını söylüyor.
- **Boş hücre iki anlama geliyor.** Bir ay tabloda herhangi bir kalemde doluysa o ay yayımlanmıştır ve boş hücre "harcama yok" demektir, 0 yazılır. Hiçbir kalemde dolu olmayan aylar henüz yayımlanmamıştır, tabloya girmez.
- **Kurumsal tabloda kurum listesinden sonra özet satırları var:** özel bütçeli idareler, düzenleyici kurumlar, merkezi yönetim toplamı. Okuma, kurum toplamı satırında bitiyor.
- **Kurum adlarının yazımı değişiyor:** "Hazine Ve Maliye" / "Hazine ve Maliye".

### Kontroller

`clean.py` her çalıştığında üç kontrolü yapıyor ve biri tutmazsa duruyor:

1. **Satır toplamı:** her satırda 12 ayın toplamı, dosyanın kendi "Toplam" sütununa eşit mi?
2. **Kurum toplamı:** okunan kurumların toplamı, tablodaki kurum toplamı satırına eşit mi?
3. **Mutabakat:** gider detay tablosundaki dokuz ana kalem, denge tablosundaki aynı kalemlerle aynı tutarı mı veriyor? İki tablo ayrı yayımlandığı için bu, doğru satırların okunduğunun bağımsız kanıtı. 1.368 nokta karşılaştırılıyor.

## Kurulum

*(3. gün sonunda yazılacak)*

## Kullanım

*(5. gün sonunda yazılacak)*

## Rapor

*(6. gün sonunda yazılacak)*

## Proje yapısı

```
hazine-nabzi/
├── download.py        Muhasebat'tan 2015–2026 tablolarını indirir
├── clean.py           Ham dosyaları temizleyip iki tabloya çevirir, kontrolleri yapar
├── xls_reader.py      Eski .xls dosyalarını okur (bozuk biçim kayıtlarını atlar)
├── items.csv          Gider detayından alınacak kalemler, eski adlarıyla birlikte
├── requirements.txt   Gerekli Python kütüphaneleri
├── KURALLAR.md        Projenin çalışma kuralları ve günlüğü
└── data/
    ├── raw/           İndirilen ham dosyalar (repoya dahil değil)
    └── clean/         Temizlenmiş tablolar: actuals.csv, plans.csv
```
