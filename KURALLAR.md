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
| 4 | SQL hesapları: sapma, kümülatif gerçekleşme, en çok sapan kalemler |
| 5 | Tek komutla çalışan akış: indir → temizle → yükle → hesapla |
| 6 | Power BI: Power Query, DAX ölçüleri, tek sayfalık rapor |
| 7 | README'nin son hali, GitHub'a yükleme, CV maddeleri |

## Günlük

- **18.09.2026:** Proje klasörü ve kurallar oluşturuldu. Proje adı: Hazine Nabzı. Veri kaynağına erişim doğrulandı: Muhasebat'ın 2015–2026 bütçe tabloları indirilebiliyor, planlanan ödenek ve aylık gerçekleşme aynı tabloda var.
- **19.09.2026 (1. gün):** İki dilli README kuruldu, kod dilinin İngilizce olmasına karar verildi. `download.py` ve `xls_reader.py` yazıldı; 2015–2026 için üç tablo (denge, gider detayı, bakanlıklar) toplam 36 dosya iniyor. Formatlar 12 yıl boyunca karşılaştırıldı: denge tablosu tutarlı, gider detayında plan sütunu da var ve ana tabloyla birebir tutuyor. Kapsama bakanlıklar eklendi. Gider detayından 23 kalem seçildi (`items.csv`); 2021 öncesinde ayrı satırı olmayan SSK 5 puan indirimi ve KİT sermaye çıkarıldı.
- **20.09.2026 (2. gün):** `clean.py` yazıldı: 36 ham dosya iki uzun biçim tabloya dönüşüyor (`data/clean/actuals.csv` 13.728 satır, `plans.csv` 1.174 satır). Sütunlar adıyla bulunuyor, 2021'de değişen kalem adları `items.csv`'deki `old_name` ile eşleşiyor, aynı adın tekrarı `search_under` ile çözülüyor. Üç otomatik kontrol eklendi (satır toplamı, kurum toplamı, iki tablo arası mutabakat); kontroller iki gerçek hata yakaladı: 2015 kurumsal dosyasındaki özet satırları kurum sanılıyordu, 2022'de yedek ödenek satırı tamamen boş olduğu için düşüyordu. Boş hücre kuralı: ay yayımlanmışsa 0, yayımlanmamışsa satır yok. Kod yazımı Claude'a geçti, kararlar Atakan'da (4. kural).
- **20.09.2026 (3. gün):** SQL Server 2025 Express (instance `SQLEXPRESS`) Windows'a kuruldu. WSL'den bağlanabilmek için üç ayar açıldı: SQL kullanıcı girişi, TCP/1433 ve güvenlik duvarı izni; `hazine_nabzi` veritabanı ve `hazine` kullanıcısı oluşturuldu. Tablo tasarımı: iki tablo, CSV'lerle aynı yapı, tipli ve birincil anahtarlı (anahtar aynı kalemin iki kez girmesini engelliyor). `load.py` yazıldı: tabloları sıfırlayıp yeniden dolduruyor, yazılan satır sayısını tablodakiyle karşılaştırıyor. 13.728 + 1.174 satır 7 saniyede yüklendi; CSV ile SQL toplamları 1.176 kalem grubunda birebir aynı. Tutar tipi DECIMAL(19,5) — ilk denemede (18,3) yuvarlama farkı yaratmıştı. Şifre `.env`'de, repoya girmiyor; `.env.example` eklendi.

