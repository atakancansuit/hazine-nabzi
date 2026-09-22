# Proje kuralları

Bu dosya projenin nasıl yürütüleceğini anlatır. Proje boyunca her yeni kural, tarihiyle birlikte buraya eklenir.

## 1. Okunabilirlik her şeyden önce gelir

Repoyu ilk kez açan biri, yalnızca README'yi okuyarak üç şeyi anlayabilmeli:

- **Ne:** proje ne yapıyor, hangi soruya cevap veriyor.
- **Nasıl kurulur:** hangi programlar gerekli, hangi sırayla kurulur.
- **Nasıl kullanılır:** tek komutla nasıl çalıştırılır, çıktılar nerede.

README her gün, o günün işiyle birlikte güncellenir. Kod README'den önde gitmez.

README iki dilde tutulur: `README.md` İngilizce (GitHub bunu gösterir), `README.tr.md` Türkçe. İkisinin en üstünde diğerine link olur. Gün içinde Türkçe yazılır; akşam temize çekerken İngilizcesi çıkarılır, iki dosya aynı gün güncellenir.

## 2. Basit kalır

- Her dosyanın tek bir görevi vardır. Görevi dosya adından anlaşılır.
- Klasör sayısı az tutulur. Bir klasör gerçekten gerekmedikçe açılmaz.
- Kullanılmayan kod, deneme dosyası ve eski sürüm repoda kalmaz. Git geçmişi zaten saklıyor.
- Yeni bir araç, kütüphane ya da adım eklemeden önce şu soru sorulur: bu olmadan olur mu?

README'de her bilgi kendi başlığında durur. "Veri" bölümü yalnızca kaynağı ve kapsamı anlatır. Temizlikte ne yapıldığı ileride açılacak bir temizlik bölümüne, veriden çıkan bulgular sonuç bölümüne yazılır. Birim gibi bilgiler tablonun kendisinde (sütun adında ya da parantez içinde) gösterilir. *(19.09.2026)*

Kod İngilizce yazılır: dosya, klasör, tablo, sütun ve değişken adları İngilizce olur (`download.py`, `actual`, `planned`). Kod içindeki açıklamalar Türkçe olabilir. *(19.09.2026)*

## 3. Her gün sonunda temize çekilir

Günün işi bittiğinde, commit'ten önce:

1. Deneme hücreleri, geçici dosyalar ve kullanılmayan kod silinir.
2. Kodu baştan sona bir kez çalıştırıp hatasız bittiği görülür.
3. Dosya ve değişken adları anlaşılır mı, bakılır.
4. README güncellenir, Türkçe ve İngilizce.
5. Bu dosyanın sonundaki "Günlük" bölümüne o gün ne yapıldığı bir iki satırla yazılır.
6. Anlamlı bir mesajla commit atılır.

## 4. Kim ne yazar

- **Claude yazar:** dosya indirme, Excel'in dağınık başlıklarını ayıklama, klasör iskeleti gibi mülakatta anlatılmayacak kısımlar.
- **Atakan yazar:** temizlik, hesaplama ve raporlama KARARLARI. Hangi kalem alınır, hangi satır atılır, hangi ölçü hesaplanır.
- **Kodun kendisini Claude yazar** *(19.09.2026 kararı)*, Atakan yapıştırır. Claude her parçanın ne yaptığını anlatır; amaç kodu ezberlemek değil, mülakatta mantığını anlatabilmek.

---

## Plan

| Gün | İş |
|---|---|
| 1 | Veriyi tanımak: üç dosya türü (denge tablosu, gider detayı, bakanlıklar) 2015–2026 için indirilir, formatları karşılaştırılır, gider detayından alınacak kalemler seçilir |
| 2 | Python ile temizleme: dağınık Excel'den düzgün tabloya |
| 3 | SQL Server Express kurulumu ve temiz tabloların yüklenmesi |
| 4 | SQL hesapları: sapma, kümülatif gerçekleşme, en çok sapan kalemler, yıl sonu tahmini. View ve stored procedure olarak |
| 5 | Tek komutla çalışan akış (indir → temizle → yükle → hesapla) ve aylık zamanlayıcı |
| 6 | Power BI: Power Query, DAX ölçüleri, tek sayfalık rapor |
| 7 | Otomatik Excel yönetim raporu: aynı rakamlardan biçimli bir .xlsx |
| 8 | Yönetim yorumu: rakamlardan kısa bir özet metni üreten LLM adımı |
| 9 | README'nin son hali, GitHub'a yükleme, CV maddeleri |

*(Plan 20.09.2026'da 7 günden 9 güne çıkarıldı: Excel raporu, zamanlayıcı ve LLM yorumu
ilk kapsam daraltmasında çıkarılmıştı, tempo iyi gidince geri eklendi. Atakan: "baştan
sona fıstık gibi bir rapor olsun".)*

## Günlük

- **18.09.2026:** Proje klasörü ve kurallar oluşturuldu. Proje adı: Hazine Nabzı. Veri kaynağına erişim doğrulandı: Muhasebat'ın 2015–2026 bütçe tabloları indirilebiliyor, planlanan ödenek ve aylık gerçekleşme aynı tabloda var.
- **19.09.2026 (1. gün):** İki dilli README kuruldu, kod dilinin İngilizce olmasına karar verildi. `download.py` ve `xls_reader.py` yazıldı; 2015–2026 için üç tablo (denge, gider detayı, bakanlıklar) toplam 36 dosya iniyor. Formatlar 12 yıl boyunca karşılaştırıldı: denge tablosu tutarlı, gider detayında plan sütunu da var ve ana tabloyla birebir tutuyor. Kapsama bakanlıklar eklendi. Gider detayından 23 kalem seçildi (`items.csv`); 2021 öncesinde ayrı satırı olmayan SSK 5 puan indirimi ve KİT sermaye çıkarıldı.
- **20.09.2026 (2. gün):** `clean.py` yazıldı: 36 ham dosya iki uzun biçim tabloya dönüşüyor (`data/clean/actuals.csv` 13.728 satır, `plans.csv` 1.174 satır). Sütunlar adıyla bulunuyor, 2021'de değişen kalem adları `items.csv`'deki `old_name` ile eşleşiyor, aynı adın tekrarı `search_under` ile çözülüyor. Üç otomatik kontrol eklendi (satır toplamı, kurum toplamı, iki tablo arası mutabakat); kontroller iki gerçek hata yakaladı: 2015 kurumsal dosyasındaki özet satırları kurum sanılıyordu, 2022'de yedek ödenek satırı tamamen boş olduğu için düşüyordu. Boş hücre kuralı: ay yayımlanmışsa 0, yayımlanmamışsa satır yok. Kod yazımı Claude'a geçti, kararlar Atakan'da (4. kural).
- **20.09.2026 (3. gün):** SQL Server 2025 Express (instance `SQLEXPRESS`) Windows'a kuruldu. WSL'den bağlanabilmek için üç ayar açıldı: SQL kullanıcı girişi, TCP/1433 ve güvenlik duvarı izni; `hazine_nabzi` veritabanı ve `hazine` kullanıcısı oluşturuldu. Tablo tasarımı: iki tablo, CSV'lerle aynı yapı, tipli ve birincil anahtarlı (anahtar aynı kalemin iki kez girmesini engelliyor). `load.py` yazıldı: tabloları sıfırlayıp yeniden dolduruyor, yazılan satır sayısını tablodakiyle karşılaştırıyor. 13.728 + 1.174 satır 7 saniyede yüklendi; CSV ile SQL toplamları 1.176 kalem grubunda birebir aynı. Tutar tipi DECIMAL(19,5) — ilk denemede (18,3) yuvarlama farkı yaratmıştı. Şifre `.env`'de, repoya girmiyor; `.env.example` eklendi.
- **21.09.2026 (4. gün):** Hesaplar SQL'e taşındı. `sql/views.sql` içinde beş görünüm (`v_monthly`, `v_annual`, `v_variance_rank`, `v_year_end_forecast`, `v_forecast_backtest`), `sql/procedures.sql` içinde `sp_monthly_report`, `sql/examples.sql` içinde yedi örnek sorgu; hepsini `apply_sql.py` uyguluyor. Önce raporun tek sayfalık taslağı çizildi, görünümler ona göre yazıldı. Yıl sonu tahmini rolling forecast mantığıyla: geçmiş yılların aynı aya kadarki payı bu yılın kümülatifine uygulanıyor, böylece Aralık yığılması hesaba katılıyor. Tahmin geriye dönük test edildi (o yılın kendi verisi hariç tutularak): medyan hata 4 ayda %11,4, 8 ayda %5,9, 10 ayda %3,4. `plan` SQL Server'da ayrılmış kelime olduğu için sütun adı `planned` oldu.
- **21.09.2026 (5. gün):** `run.py` yazıldı: indir → temizle → yükle → hesapla zinciri tek komutta, baştan sona 31 saniye. Çıktı hem ekrana hem `logs/<tarih>.log` dosyasına yazılıyor, bir adım hata verirse akış duruyor ve sıfırdan farklı çıkış kodu veriyor. `logs/` repoya girmiyor. Windows Görev Zamanlayıcı'ya aylık görev kuruldu (her ayın 20'si 09:00, `wsl.exe -d Ubuntu -- .venv/bin/python run.py`; kaçırılan çalıştırmalar için "en kısa sürede yeniden çalıştır" açık). `v_monthly`'ye kıyas sütunu eklendi (`typical_pct_of_plan`): geçmiş yıllarda aynı ayda planın yüzde kaçı gerçekleşmişti. Kıyas, bitmemiş yılda "%64 az mı çok mu" sorusunu cevaplıyor. Ayrıca denge satırlarında (bütçe dengesi, faiz dışı denge) yüzde hesabı tamamen kapatıldı; planları sıfıra yakın olduğu için oran binleri buluyordu.
- **21-22.09.2026 (6. gün):** Power BI raporunun beş sayfası kuruldu: Özet (4 kart + kümülatif gidiş), Kalemler, Kurumlar, Yöntem (tahmin hatası eğrisi + kalem bazında hata) ve drill-through ile açılan Kalem detayı. Model yıldız şema: `sql/dimensions.sql` ile `dim_year` ve `dim_item` eklendi, hesap görünümlerine `item_key` konuldu, sekiz ilişki kuruldu. `dim_item`'a `display_name` (hiyerarşi işaretlerinden arındırılmış ad) ve `is_total` (toplam mı alt kalem mi) sütunları eklendi; ikincisi olmadan grafikler aynı parayı iki kez sayıyordu. 11 DAX ölçüsü yazıldı. `v_forecast_backtest` Power BI'a yüklenemeyecek kadar yavaştı (her satır için tablo yeniden taranıyordu); kendisi hariç ortalama tek geçişte toplayıp çıkarma yöntemiyle yeniden yazıldı, sonuç aynı, süre 1,8 saniyeye indi. Rapor `.pbip` (Power BI Project) biçiminde `powerbi/` altına kaydedildi: metin dosyalarından oluştuğu için hem git'te okunabiliyor hem de görsellerin başlığı, altyazısı, rengi ve konumu doğrudan dosyadan düzenlenebiliyor. 19 görselin başlığı ve altyazısı, 12 ölçünün açıklaması, sayfa yerleşimleri ve tema bu yolla yazıldı. Tema Muhasebat'ın kurumsal renklerini kullanıyor (lacivert #222d56, altın #c7a069); tuval lacivert, görseller beyaz kart. Her sayfanın altına iki bölümlü açıklama metni eklendi: "nasıl okunur" ve o sayfanın bulguları. Yöntem sayfasına ölçü tanımları kutusu kondu. Kalemler ve Kurumlar sayfaları bitmiş yıl olan 2025 ile açılıyor. Ekran görüntüleri `docs/` altında, README'nin Rapor bölümü iki dilde yazıldı.
  **Ders (iki kez yaşandı):** Power BI açıkken dosyaya dışarıdan yazmak işe yaramıyor; program açtığı andaki hali gösteriyor ve kaydettiğinde diskteki düzenlemeleri eziyor. Sıra: önce Power BI kapanır, sonra dosya düzenlenir, sonra açılır. Ayrıca `.pbip` dosyasının kendisi 185 baytlık bir işaretçi; içerik `.Report` ve `.SemanticModel` klasörlerinde, dolayısıyla `.pbip`'in tarihine bakmak yanıltıyor.
- **22.09.2026 (7. gün):** `excel_report.py` yazıldı: SQL görünümlerinden dört sayfalık biçimli bir Excel raporu üretiyor (Özet, Kalemler, Kurumlar, Aylık). Lacivert başlık şeridi, binlik ayırıcı, yüzde biçimi, donmuş başlık satırı, planı aşanlarda kırmızı ve altında kalanlarda yeşil yazı. Dosya `reports/rapor_<yıl>-<ay>.xlsx`; klasör `.gitignore`'da, örnek çıktı `docs/ornek-rapor.xlsx` olarak repoda. `run.py`'ye beşinci adım olarak eklendi, akış artık 12 saniye. Not: `apply_sql` görünümleri yeniden oluşturduğu için sorgu planları sıfırlanıyor ve ilk Excel adımı bir kereye mahsus dakikalarca sürebiliyor; ikinci çalıştırmada 1,3 saniyeye iniyor. `excel_report.main()` artık komut satırını kendisi okumuyor, `run.py`'den çağrılabilmesi için yıl parametresi alıyor.
- **22.09.2026 (8. gün):** Akış yorum ve e-posta adımlarıyla tamamlandı. `commentary.py` ayın rakamlarını veritabanından alıp tek metne çeviriyor ve Claude'a (`claude-opus-5`, effort low) yorumlatıyor; sistem yönergesi "yalnızca verilen rakamları kullan, sebep uydurma, yıl bitmemişse belirt" diyor. Üretilen yorumdaki bütün rakamlar SQL'den doğrulandı, uydurma yok. Maliyet çalıştırma başına ~1,5 sent (1.979 girdi + 968 çıktı jetonu). `send_mail.py` yorumu gövdeye, Excel raporunu eke koyup Gmail üzerinden gönderiyor (SMTP SSL, uygulama şifresi `.env`'de). `run.py` yedi adıma çıktı, baştan sona 65 saniye. E-posta ekran görüntüsü `docs/eposta.png`, README'ye iki dilde eklendi. Not: SQL'de `plan` ayrılmış kelime olduğu için takma ad yine hata verdi (`planlanan` yapıldı) — bu üçüncü tekrarı.
