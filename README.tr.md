[English](README.md) | **Türkçe**

# Hazine Nabzı

> Proje yapım aşamasında. Bu dosya her gün, o günün işiyle birlikte doldurulacak.

Türkiye merkezi yönetim bütçesinde yıl başında planlanan tutarlarla ay ay gerçekleşen tutarları karşılaştıran, otomatik çalışan bir raporlama projesi.

## Ne yapıyor

Bir finans ekibinin her ay yaptığı işi otomatikleştiriyor: planlanan bütçe ile gerçekleşen harcamayı karşılaştırmak, sapmaları bulmak ve raporlamak.

Veri, Hazine ve Maliye Bakanlığı Muhasebat Genel Müdürlüğü'nün her ay yayımladığı bütçe tabloları. Proje bu tabloları kendisi indiriyor, temizliyor, veritabanına yüklüyor ve Power BI raporuna dönüştürüyor.

Cevapladığı sorular:

1. Hangi harcama ve gelir kalemleri plandan en çok sapıyor?
2. Hangi bakanlık bütçesini aştı, hangisi altında kaldı?
3. Sapma yılın hangi ayında ortaya çıkıyor?
4. Bu tablo yıldan yıla tekrar ediyor mu?
5. Yılın ilk aylarına bakarak yıl sonu tahmin edilebilir mi?

## Veri

**Kaynak:** [Muhasebat Genel Müdürlüğü, Merkezi Yönetim Bütçe İstatistikleri](https://muhasebat.hmb.gov.tr/merkezi-yonetim-butce-istatistikleri).

**Kapsam:** 2015–2026, aylık. 2026 yılı yayımlanan son aya kadar.

Her yıl için üç tablo kullanılıyor:

| Tablo | İçerik | Satır |
|---|---|---|
| Bütçe denge tablosu | Gelir ve giderin ana kalemleri, bütçe açığı | 23 kalem |
| Gider detay tablosu | Giderlerin alt kalemleri | 23 seçilmiş kalem ([`items.csv`](items.csv)) |
| Kurumsal tablo | Bakanlıklar ve diğer genel bütçeli kurumlar | 41–52 kurum |

Üç tabloda da her kalem için 12 ayın gerçekleşmesi ve yıl başındaki plan var. Plan, Meclis'in onayladığı Bütçe Kanunu'ndaki başlangıç ödeneği.

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
├── xls_reader.py      Eski .xls dosyalarını okur (bozuk biçim kayıtlarını atlar)
├── items.csv          Gider detayından alınacak kalemlerin listesi
├── requirements.txt   Gerekli Python kütüphaneleri
├── KURALLAR.md        Projenin çalışma kuralları ve günlüğü
└── data/raw/          İndirilen ham dosyalar (repoya dahil değil)
```
