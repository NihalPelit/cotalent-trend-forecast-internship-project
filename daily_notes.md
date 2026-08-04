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


## Day 2 — 04.08.2026

### Hedefler

- Pytrends veri çekme kodunu tekrar kullanılabilir bir fonksiyona dönüştürmek
- Hata yönetimi ve input validation eklemek
- Google Trends verisini raw olarak kaydetmek
- Preprocessing işlemlerini başlatmak
- Temiz veriyi processed olarak kaydetmek
- İlk EDA ve görselleştirme işlemlerini yapmak
- Pytrends çıktısını Google Trends web arayüzü ile doğrulamak

### Yapılan Çalışmalar

#### 1. Veri Çekme Fonksiyonu

`src/fetch_data.py` içerisinde tekrar kullanılabilir
`fetch_trends_data()` fonksiyonu oluşturuldu.

Fonksiyona:

- type hint
- docstring
- keyword validation
- hata yönetimi

eklendi.

Boş keyword listesi için `ValueError`, string olmayan keyword değerleri
için `TypeError` kullanılmaktadır.

#### 2. API Hata Yönetimi

Google Trends sorguları sırasında:

- HTTP 429 Too Many Requests
- HTTP 400 Bad Request

hataları gözlemlendi.

`TooManyRequestsError` ve `ResponseError` kontrollü şekilde yönetildi.

429 hataları için retry ve exponential backoff mekanizması oluşturuldu.

Retry sırasında istekler arasında sırasıyla artan bekleme süreleri
kullanıldı.

#### 3. Veri Setinin Oluşturulması

Aşağıdaki Google Trends keyword'leri aynı sorgu içerisinde karşılaştırıldı:

- chatgpt
- gemini
- claude

Parametreler:

- Region: Worldwide
- Time range: yaklaşık son 3 yıl
- Frequency: Weekly

Başarıyla çekilen veri raw CSV olarak kaydedildi.

#### 4. Preprocessing

`src/preprocess.py` oluşturuldu.

Google Trends verisindeki `isPartial=True` satırlar kaldırıldı.

Eksik değer kontrolü sonucunda:

- chatgpt: 0 eksik değer
- gemini: 0 eksik değer
- claude: 0 eksik değer

bulundu.

Tarih aralıkları kontrol edildi ve bütün gözlemler arasında 7 günlük
düzenli aralık bulundu.

Bu nedenle veri setinde eksik hafta olmadığı görüldü ve interpolation
uygulanmasına gerek kalmadı.

`isPartial` sütunu temiz veri setinden kaldırıldı.

Temiz veri:

`data/processed/google_trends_ai_3y_clean.csv`

olarak kaydedildi.

#### 5. Exploratory Data Analysis

Temiz veri Pandas ile tekrar yüklendi.

Aşağıdakiler kontrol edildi:

- 157 non-null observation
- numeric column types
- DatetimeIndex
- missing values

Matplotlib kullanılarak ChatGPT, Gemini ve Claude trendleri aynı grafik
üzerinde görselleştirildi.

Grafikte:

- ChatGPT'nin genel olarak en yüksek ilgiye sahip olduğu
- Gemini'nin belirgin bir spike gösterdiği
- Claude'un özellikle son dönemde yükseliş gösterdiği

gözlemlendi.

#### 6. Pytrends Verisinin Doğrulanması

Pytrends ile alınan verinin doğruluğunu kontrol etmek amacıyla aynı:

- keyword'ler
- coğrafya
- zaman aralığı
- Web Search ayarları

Google Trends web arayüzünde karşılaştırıldı.

Google Trends web çıktısının aylık, pytrends çıktısının ise haftalık olduğu
görüldü.

Haftalık pytrends verisi:

`resample("MS").mean()`

ile aylık seviyeye dönüştürüldü.

Aylıklaştırılmış pytrends verisinin Google Trends web verisi ile genel trend
ve spike davranışları açısından yakın olduğu gözlemlendi.

Değerlerin birebir aynı olması beklenmemektedir çünkü Google Trends
normalizasyonu veri granülaritesine ve sorguya göre yeniden hesaplanabilir.

### Bugün Öğrenilen Kavramlar

- Python module ve import
- Type hint
- Docstring
- Input validation
- ValueError ve TypeError
- try / except
- raise
- HTTP 400 ve 429
- Retry
- Exponential backoff
- `time.sleep()`
- Raw ve processed data
- `pd.read_csv()`
- `index_col`
- `parse_dates`
- Boolean filtering
- `~` operatörü
- `.copy()`
- `.drop()`
- `DatetimeIndex`
- Matplotlib
- EDA
- `max()` ve `idxmax()`
- `resample()`
- Haftalık ve aylık veri granülaritesi

### Sonraki Adımlar

- Pytrends ve Google Trends web verisini sayısal olarak daha detaylı
  karşılaştırmak
- Trend ve seasonality decomposition yapmak
- Preprocessing kodunu geliştirmek
- Modelleme aşamasına hazırlık yapmak