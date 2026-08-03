# Staj Günlüğü

## Gün 1 — 03.08.2026

### Bugünkü Hedef

* Proje dokümanını incelemek
* Geliştirme ortamını hazırlamak
* Pytrends'i tanımak
* Google Trends'ten ilk zaman serisi verisini çekmek

### Yapılanlar

* Proje için sanal ortam oluşturuldu.
* Gerekli temel Python kütüphaneleri yüklendi.
* Tüm denemeler jupyter notebook' da yapıldı.
* Pytrends kütüphanesindeki `TrendReq` sınıfı incelendi.
* `build_payload()` metodunun parametreleri öğrenildi.
* `interest_over_time()` ile Google Trends zaman serisi verisi çekildi.
* Türkiye için `geo="TR"` ve `tz=180` kullanıldı.
* Java, Python ve C++ kelimeleriyle test sorgusu oluşturuldu.
* Gelen veri Pandas DataFrame olarak incelendi.
* `head()`, `shape`, `info()`, `describe()` gibi temel Pandas araçları kullanıldı.
* Eksik değer kontrolü yapıldı.
* Haftalık zaman serisinde eksik tarih olup olmadığı kontrol edildi.
* Son haftanın `isPartial=True` olduğu görüldü.
* Gerçek veriden bir değer bilinçli olarak `NaN` yapılarak linear interpolation denendi.
* Gerçek değer ile interpolation sonucu arasındaki hata karşılaştırıldı.

### Öğrendiklerim

* Google Trends mutlak arama sayısı yerine 0–100 arasında normalize edilmiş ilgi değerleri sağlar.
* `TrendReq`, Google Trends isteklerini yöneten sınıftır.
* `build_payload()` sorgu parametrelerini hazırlar.
* `interest_over_time()` zaman içerisindeki ilgi verisini DataFrame olarak döndürür.
* DataFrame iki boyutlu, Series ise tek boyutlu bir Pandas veri yapısıdır.
* `.loc` etiket kullanarak belirli satır ve sütunlara erişmek için kullanılabilir.
* `NaN` eksik değeri temsil eder.
* Eksik hücre ile tamamen eksik bir tarih aynı şey değildir.
* Linear interpolation komşu değerlerin arasında doğrusal bir değişim varsayarak eksik değer tahmini yapar.
* Bir Pandas işleminin sonucunu değişkene geri atamadığımız sürece orijinal veri otomatik olarak değişmeyebilir.

### Sonuç

İlk gün oryantasyon ve temel Pytrends denemeleri tamamlandı. Sonraki aşamada kullanılacak gerçek teknoloji/keyword seti netleştirildikten sonra veri toplama ve preprocessing pipeline'ı geliştirilecek.
