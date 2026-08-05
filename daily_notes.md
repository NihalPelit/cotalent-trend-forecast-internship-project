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

## Day 3 — 05.08.2026

### Hedefler

- Zaman serisi decomposition mantığını öğrenmek
- Trend, seasonal ve residual bileşenlerini incelemek
- ChatGPT zaman serisini detaylı olarak analiz etmek
- Büyük residual değerlerini tespit etmek ve dış olaylarla karşılaştırmak
- ChatGPT, Gemini ve Claude uzun vadeli trendlerini karşılaştırmak
- Decomposition kodunu tekrar kullanılabilir fonksiyonlara dönüştürmek
- Zaman serisi işlemlerini `src` klasörüne taşımak
- Proje bağımlılıklarını güncellemek

### Yapılan Çalışmalar

#### 1. Time Series Decomposition

`statsmodels` kütüphanesi projeye eklendi.

Decomposition işlemi için:

`statsmodels.tsa.seasonal.seasonal_decompose`

kullanıldı.

Haftalık Google Trends verileri üzerinde:

- Model: Additive
- Period: 52

parametreleri kullanıldı.

`period=52` ile haftalık veride yaklaşık yıllık bir tekrar yapısı
varsayılarak decomposition uygulandı.

Zaman serisi aşağıdaki bileşenlere ayrıldı:

- Observed
- Trend
- Seasonal
- Residual

Yaklaşık 3 yıllık veri bulunduğu için 52 haftalık seasonality sonucunun
kesin bir yıllık davranış olarak yorumlanmaması gerektiği not edildi.

#### 2. ChatGPT Trend Analizi

ChatGPT serisinin trend bileşeni detaylı olarak incelendi.

Trend bileşenindeki hesaplanabilir ilk ve son değerler:

- First trend: yaklaşık `20.32`
- Last trend: yaklaşık `73.73`

olarak bulundu.

Bu sonuç ChatGPT'nin incelenen dönem içerisinde uzun vadeli Google Trends
ilgi seviyesinin önemli ölçüde arttığını gösterdi.

Trend grafiğinin son bölümünde artış hızının önceki dönemlere göre
yavaşladığı ve yüksek seviyede daha yatay bir davranış oluşmaya başladığı
gözlemlendi.

Decomposition yönteminin seri başlangıcı ve sonunda trend değerlerini
hesaplayamadığı ve bu bölgelerde `NaN` oluşturmasının yöntemin doğal bir
sonucu olduğu incelendi.

#### 3. Seasonal Bileşen Analizi

ChatGPT'nin seasonal bileşeni incelendi.

Bulunan yaklaşık değerler:

- Maximum seasonal: `+11.04`
- Minimum seasonal: `-18.42`

En yüksek seasonal değer:

- 2024-03-31

En düşük seasonal değer:

- 2023-12-31

civarında gözlemlendi.

52 haftalık periyot kullanıldığı için aynı yıl içi konumlardaki seasonal
değerlerin tekrar eden bir yapı göstermesi incelendi.

Seasonal bileşenin tek başına gerçek olayların nedeni olmadığı, decomposition
modelinin veriden çıkardığı tekrarlayan yapı olduğu not edildi.

#### 4. Residual Analizi

Trend ve seasonal bileşenlerle açıklanamayan hareketleri incelemek amacıyla
residual değerleri analiz edildi.

Mutlak residual değeri en büyük haftalar belirlendi.

Öne çıkan residual değerleri:

- 2025-03-30 → `+13.49`
- 2024-03-31 → `-12.59`
- 2025-09-14 → `+8.56`
- 2025-08-03 → `+7.69`
- 2024-09-15 → `-7.66`

Pozitif residual değerinin:

`observed > trend + seasonal`

durumunu,

negatif residual değerinin ise:

`observed < trend + seasonal`

durumunu ifade ettiği incelendi.

Residual değerlerin yüzde olmadığı, Google Trends ölçeği üzerindeki
açıklanamayan sapmaları temsil ettiği not edildi.

#### 5. Decomposition Sonuçlarının DataFrame'e Dönüştürülmesi

Decomposition sonucundaki bileşenler tek bir Pandas DataFrame içerisinde
birleştirildi.

Oluşturulan sütunlar:

- observed
- trend
- seasonal
- residual

Ayrıca:

`expected = trend + seasonal`

hesaplanarak `expected` sütunu oluşturuldu.

Bu yapı sayesinde gerçek Google Trends değeri ile decomposition'ın trend ve
seasonality temelindeki değeri aynı satır üzerinde karşılaştırılabilir hale
geldi.

Trend değeri `NaN` olan seri başlangıcı ve sonundaki satırlarda residual ve
expected değerlerinin de `NaN` olmasının normal olduğu görüldü.

#### 6. Büyük Residual Tarihlerinin Araştırılması

Yüksek mutlak residual değerlerinin bulunduğu haftaların çevresindeki dış
gelişmeler araştırıldı.

OpenAI'nin resmi duyuruları ve ilgili teknoloji gelişmeleri residual
tarihleriyle karşılaştırıldı.

Özellikle bazı pozitif residual dönemlerinin büyük ürün duyuruları ve
ChatGPT ile ilgili yoğun ilgi dönemleriyle zaman açısından örtüştüğü görüldü.

Negatif residual bulunan bazı dönemlerde de önemli duyurular bulunabildiği
gözlemlendi.

Bu nedenle:

- Büyük bir duyurunun mutlaka pozitif residual oluşturmadığı
- Residual analizinin nedensellik kanıtlamadığı
- Residual değerlerinin sıra dışı dönemleri araştırmak için bir sinyal olarak
  kullanılabileceği

sonucuna ulaşıldı.

#### 7. ChatGPT, Gemini ve Claude Trend Karşılaştırması

Aynı decomposition işlemi:

- chatgpt
- gemini
- claude

serilerine uygulandı.

Her seri için hesaplanabilir ilk ve son trend değerleri çıkarıldı.

Sonuçlar:

| AI | First Trend | Last Trend | Trend Change |
|---|---:|---:|---:|
| chatgpt | 20.32 | 73.73 | +53.41 |
| gemini | 2.59 | 37.28 | +34.69 |
| claude | 1.06 | 9.74 | +8.68 |

`trend_change` değeri:

`last_trend - first_trend`

şeklinde hesaplandı.

Sonuçlara göre:

- ChatGPT hem başlangıçta hem dönem sonunda en yüksek trend seviyesine sahip
  oldu.
- ChatGPT yaklaşık `+53.41` ile en yüksek mutlak trend artışını gösterdi.
- Gemini düşük bir başlangıç seviyesinden yaklaşık `+34.69` trend artışına
  ulaştı.
- Claude da yükseliş gösterdi ancak hem trend seviyesi hem de mutlak artışı
  diğer iki seriden daha düşük kaldı.

Google Trends değerlerinin gerçek arama sayıları değil, normalize edilmiş
ilgi değerleri olduğu dikkate alındı.

#### 8. Decomposition Kodunun Modüler Hale Getirilmesi

Notebook içerisinde test edilen decomposition işlemleri tekrar kullanılabilir
hale getirildi.

`src/time_series.py`

dosyası oluşturuldu.

Bu dosya içerisinde:

`decompose_series()`

fonksiyonu geliştirildi.

Fonksiyon:

- Pandas Series kabul etmektedir
- decomposition modelini parametre olarak alabilmektedir
- period değerini parametre olarak alabilmektedir
- `DecomposeResult` döndürmektedir

Notebook'taki eski decomposition sonucu ile `src` içerisindeki fonksiyonun
ürettiği sonuç karşılaştırıldı.

Pandas `.equals()` kullanılarak sonuçların aynı olduğu doğrulandı.

#### 9. Decomposition DataFrame Fonksiyonu

`src/time_series.py` içerisine:

`decomposition_to_dataframe()`

fonksiyonu eklendi.

Bu fonksiyon `DecomposeResult` nesnesini aşağıdaki sütunlardan oluşan bir
DataFrame'e dönüştürmektedir:

- observed
- trend
- seasonal
- residual
- expected

Böylece notebook içerisinde aynı DataFrame oluşturma kodunun tekrar tekrar
yazılmasına gerek kalmadı.

#### 10. Notebook ve `src` Entegrasyonu

Notebook'un `notebooks/` klasöründe, Python kaynak dosyalarının ise `src/`
klasöründe bulunması nedeniyle import yolu problemiyle karşılaşıldı.

Python'un proje kökünü görebilmesi için:

`sys.path.append("..")`

kullanıldı.

Böylece:

`from src.time_series import ...`

şeklinde proje içerisindeki fonksiyonların notebook'tan kullanılabilmesi
sağlandı.

Notebook açıkken `time_series.py` dosyasına sonradan eklenen fonksiyonların
hemen görülmeyebildiği gözlemlendi.

Bu durumda Python'un daha önce yüklediği modülü bellekte tuttuğu öğrenildi ve
gerektiğinde `importlib.reload()` ile modülün yeniden yüklenebileceği
incelendi.

#### 11. Requirements Güncellemesi

Day 3 içerisinde `statsmodels` ve gerekli bağımlılıklar kuruldu.

Sanal ortam içerisindeki güncel paketleri proje bağımlılık dosyasına aktarmak
için:

`pip freeze > requirements.txt`

komutu kullanıldı.

`requirements.txt` içerisinde `statsmodels` paketinin bulunduğu kontrol edildi.

### Bugün Öğrenilen Kavramlar

- Time series decomposition
- Observed
- Trend
- Seasonality
- Residual
- Additive decomposition
- `period=52`
- `seasonal_decompose()`
- `DecomposeResult`
- `.trend`
- `.seasonal`
- `.resid`
- `.dropna()`
- `.iloc`
- `.abs()`
- `.nlargest()`
- `max()` ve `min()`
- `idxmax()` ve `idxmin()`
- Residual yorumlama
- Expected value (`trend + seasonal`)
- Dictionary
- `for` döngüsü
- `.append()`
- Birden fazla zaman serisinin karşılaştırılması
- `trend_change`
- Fonksiyonlaştırma
- Notebook ve `src` ayrımı
- Python import path
- `sys.path`
- Python module cache
- `importlib.reload()`
- Pandas `.equals()`
- `pip freeze`
- `requirements.txt`

### Sonraki Adımlar

- Week 1 kapsamındaki preprocessing ve decomposition çalışmalarını son kez
  kontrol etmek
- Modelleme için kullanılacak hedef zaman serisini belirlemek
- Time series train/test ayrımının nasıl yapılacağını öğrenmek
- Random train/test split ile time series split arasındaki farkı incelemek
- Baseline tahmin yaklaşımı oluşturmak
- Prophet ve ARIMA modelleme aşamasına hazırlanmak
- İlerleyen aşamada tahmin performansını MAE ve RMSE ile değerlendirmek
