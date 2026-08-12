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

## Day 4 — 06.08.2026

### Hedefler

- Forecasting aşamasına giriş yapmak
- Zaman serisi verisini train ve test olarak doğru şekilde ayırmak
- Naive baseline tahmin modeli oluşturmak
- Tahmin performansını MAE ve RMSE ile değerlendirmek
- ARIMA modelinin temel mantığını öğrenmek
- Zaman serisinin durağanlığını test etmek
- Differencing işlemini uygulamak
- ARIMA için `d` parametresini belirlemek
- ACF ve PACF grafiklerini incelemek
- Farklı ARIMA parametrelerini test etmek
- ARIMA modellerini naive baseline ile karşılaştırmak

### Yapılan Çalışmalar

#### 1. Forecasting İçin Train/Test Ayrımı

Temizlenmiş ChatGPT Google Trends serisi forecasting çalışmaları için
kullanıldı.

Toplam 157 haftalık zaman serisinin:

- İlk 145 haftası train
- Son 12 haftası test

olarak ayrıldı.

Train ve test verileri zaman sırası korunarak oluşturuldu.

Train verisinin son tarihi:

`2026-05-03`

Test verisinin ilk tarihi:

`2026-05-10`

olarak bulundu.

Zaman serilerinde random train/test split kullanılmaması gerektiği incelendi.

Bunun nedeni, gelecekteki verilerin yanlışlıkla train setine girerek modelin
gelecek bilgisini önceden görmesine neden olabilmesidir.

Bu nedenle forecasting problemlerinde geçmiş verilerin train, daha sonraki
verilerin ise test olarak kullanılması gerektiği öğrenildi.

#### 2. Naive Baseline Model

Gerçek forecasting modellerini değerlendirebilmek için önce basit bir
referans model oluşturuldu.

Naive baseline yaklaşımında:

- Train serisinin son değeri alındı.
- Son bilinen değer `73` olarak bulundu.
- Test dönemindeki bütün haftalar için tahmin değeri `73` olarak kullanıldı.

Bu yaklaşım:

"Bir sonraki dönemlerde değer, en son gözlemlenen değerle aynı kalacaktır."

varsayımına dayanmaktadır.

Baseline modelin amacı gelişmiş bir tahmin üretmek değil, daha karmaşık
modellerin gerçekten iyileşme sağlayıp sağlamadığını ölçmek için referans
oluşturmaktır.

#### 3. Scikit-learn ve Model Evaluation Metrics

Tahmin performansını değerlendirmek için `scikit-learn` kütüphanesi projeye
eklendi.

Python içerisindeki import adı:

`sklearn`

olarak kullanılmaktadır.

`sklearn.metrics` modülünden:

- `mean_absolute_error`
- `root_mean_squared_error`

fonksiyonları kullanıldı.

`metrics` modülünün model tahminlerinin başarısını ölçmek için kullanılan
değerlendirme fonksiyonlarını içerdiği öğrenildi.

#### 4. MAE Hesaplaması

Naive baseline model için Mean Absolute Error (MAE) hesaplandı.

MAE:

`4.166666666666667`

yaklaşık olarak:

`4.17`

olarak bulundu.

MAE, her tahmin ile gerçek değer arasındaki mutlak farkların ortalamasını
ifade etmektedir.

Bu sonuç naive baseline modelinin gerçek Google Trends değerlerinden haftalık
olarak ortalama yaklaşık `4.17` puan saptığını göstermektedir.

Bu değerin yüzde olmadığı, Google Trends'in normalize edilmiş 0–100 ilgi
ölçeğindeki hata miktarı olduğu not edildi.

#### 5. RMSE Hesaplaması

Naive baseline model için Root Mean Squared Error (RMSE) hesaplandı.

RMSE:

`5.049752469181039`

yaklaşık olarak:

`5.05`

olarak bulundu.

RMSE hesaplamasında tahmin hatalarının kareleri kullanıldığı için büyük
hatalar MAE'ye göre daha fazla ağırlık almaktadır.

Naive baseline sonuçları:

- MAE: `4.17`
- RMSE: `5.05`

olarak kaydedildi.

#### 6. Baseline Hata Analizi

Naive baseline modelinin her test haftasındaki mutlak hataları hesaplandı.

En yüksek mutlak hata:

`8`

olarak bulundu.

En yüksek hata tarihi:

`2026-06-28`

olarak tespit edildi.

Bu tarihte:

- Actual value: `65`
- Naive prediction: `73`

olduğu için:

`|65 - 73| = 8`

puanlık hata oluştu.

Gerçek test verisi ile naive baseline tahminleri aynı grafik üzerinde
görselleştirildi.

Naive modelin sabit `73` tahmini yaptığı, gerçek serinin özellikle test
döneminin ortalarında aşağı yönlü hareket etmesi nedeniyle model hatasının
arttığı gözlemlendi.

#### 7. ARIMA Modeline Giriş

Forecasting için klasik zaman serisi modellerinden ARIMA incelendi.

ARIMA açılımı:

- AR: AutoRegressive
- I: Integrated
- MA: Moving Average

olarak ele alındı.

ARIMA modeli:

`ARIMA(p, d, q)`

şeklinde ifade edilmektedir.

Parametrelerin genel anlamları:

- `p`: geçmiş değerlerden kaç lag'in AR kısmında kullanılacağı
- `d`: serinin kaç kez differencing işleminden geçirileceği
- `q`: geçmiş tahmin hatalarından kaç lag'in MA kısmında kullanılacağı

olarak öğrenildi.

#### 8. Stationarity ve ADF Testi

ARIMA modelleme öncesinde zaman serisinin stationarity (durağanlık) durumu
incelendi.

Durağan bir serinin temel davranışının zaman boyunca çok fazla değişmemesi
gerektiği öğrenildi.

ChatGPT train serisinin grafiğinde zaman içerisinde belirgin bir yükseliş
bulunduğu için ham serinin durağan olmaması bekleniyordu.

Bu durumu istatistiksel olarak kontrol etmek için Augmented Dickey-Fuller
(ADF) testi uygulandı.

Ham train serisi için:

- ADF Statistic: `-0.9544902016340422`
- p-value: `0.7694991558514677`

bulundu.

ADF testinde null hypothesis:

"Seri durağan değildir."

olarak ele alındı.

`p-value > 0.05`

olduğu için null hypothesis reddedilemedi ve ham seri durağan kabul edilmedi.

#### 9. Differencing ve `d` Parametresi

Ham seri durağan olmadığı için birinci dereceden differencing uygulandı.

Pandas içerisinde:

`.diff()`

kullanılarak her haftanın değeri ile bir önceki haftanın değeri arasındaki
fark hesaplandı.

Differencing sonrası oluşan ilk `NaN` değer `.dropna()` ile kaldırıldı.

Bir kez fark alınmış seri için ADF testi tekrar uygulandı.

Sonuçlar:

- ADF Statistic: `-12.155582728136798`
- p-value: `1.5348088381376744e-22`

olarak bulundu.

Bu p-value değeri `0.05` değerinden çok daha küçük olduğu için null hypothesis
reddedildi ve bir kez fark alınmış seri durağan kabul edildi.

Bu nedenle ARIMA için:

`d = 1`

güçlü bir aday olarak belirlendi.

`d` parametresinin p-value'nun kendisini değil, seriyi durağanlaştırmak için
uygulanan differencing sayısını ifade ettiği öğrenildi.

#### 10. Lag Kavramı

ARIMA parametrelerinin belirlenmesi sırasında lag kavramı incelendi.

Haftalık zaman serisinde:

- Lag 1: 1 hafta önce
- Lag 2: 2 hafta önce
- Lag 3: 3 hafta önce

anlamına gelmektedir.

Lag kavramı, mevcut haftadaki değişim ile geçmiş haftalardaki değişimler
arasındaki ilişkinin incelenmesinde kullanıldı.

#### 11. ACF Analizi

Differencing uygulanmış train serisi üzerinde ACF
(Autocorrelation Function) grafiği oluşturuldu.

ACF grafiğinde:

- X ekseni lag değerlerini
- Y ekseni autocorrelation gücünü

göstermektedir.

Grafikteki güven aralığının içinde kalan küçük correlation değerlerinin
tesadüfi dalgalanmalardan kaynaklanabileceği, güven aralığının dışına çıkan
değerlerin ise daha dikkat çekici ilişkiler olabileceği incelendi.

Lag 0'ın serinin kendisiyle olan ilişkisini gösterdiği için doğal olarak `1`
olduğu ve model parametresi seçiminde dikkate alınmadığı öğrenildi.

ACF grafiğinde özellikle Lag 2 civarında negatif ve güven aralığının dışına
çıkan bir ilişki gözlemlendi.

ACF'nin ARIMA modelindeki `q` parametresi için aday değer üretmede yardımcı
olabileceği not edildi.

#### 12. PACF Analizi

Differencing uygulanmış seri üzerinde PACF
(Partial Autocorrelation Function) grafiği oluşturuldu.

PACF'nin ACF'den farklı olarak, aradaki lag'lerin etkilerini ayırdıktan sonra
belirli bir lag'in mevcut değerle doğrudan ilişkisini ölçmeye çalıştığı
öğrenildi.

PACF grafiğinde de özellikle Lag 2 dikkat çekici bulundu.

PACF'nin ARIMA modelindeki `p` parametresi için aday değer üretmede yardımcı
olabileceği incelendi.

ACF ve PACF grafiklerinin kesin `p` ve `q` değerlerini belirlemediği,
yalnızca denenmesi mantıklı parametreler için yol gösterdiği not edildi.

#### 13. ARIMA(2,1,0) Modeli

İlk ARIMA modeli:

`ARIMA(2,1,0)`

olarak oluşturuldu.

Model sadece train verisi üzerinde `.fit()` kullanılarak eğitildi.

Test döneminin uzunluğu kadar:

`12`

adım ileri tahmin üretildi.

Tahminlerin ilk haftalarda küçük değişimler gösterdiği ancak ileri
haftalarda yaklaşık `72.87` seviyesinde dengelendiği gözlemlendi.

Model performansı:

- MAE: `4.117325528903795`
- RMSE: `4.948231609916763`

olarak bulundu.

Bu model naive baseline'dan biraz daha iyi performans gösterdi.

#### 14. Farklı ARIMA Parametrelerinin Test Edilmesi

ACF ve PACF analizlerinden elde edilen adaylar doğrultusunda farklı ARIMA
konfigürasyonları test edildi.

##### ARIMA(0,1,2)

Sonuçlar:

- MAE: `3.8980385782341416`
- RMSE: `4.677279114147689`

##### ARIMA(2,1,2)

Sonuçlar:

- MAE: `4.055282453415262`
- RMSE: `4.872024282019466`

##### ARIMA(1,1,1)

Sonuçlar:

- MAE: `3.7118684310360557`
- RMSE: `4.510405278230964`

olarak bulundu.

#### 15. Model Karşılaştırması

Naive baseline ve test edilen ARIMA modelleri aynı test verisi üzerinde
MAE ve RMSE kullanılarak karşılaştırıldı.

Sonuçlar:

| Model | MAE | RMSE |
|---|---:|---:|
| ARIMA(1,1,1) | 3.71 | 4.51 |
| ARIMA(0,1,2) | 3.90 | 4.68 |
| ARIMA(2,1,2) | 4.06 | 4.87 |
| ARIMA(2,1,0) | 4.12 | 4.95 |
| Naive | 4.17 | 5.05 |

Tek 12 haftalık test dönemi üzerinde en düşük MAE ve RMSE:

`ARIMA(1,1,1)`

modelinde elde edildi.

Bu nedenle ARIMA(1,1,1) mevcut test sonuçlarına göre en başarılı aday model
olarak belirlendi.

Ancak bu model henüz nihai model olarak kabul edilmedi.

Tek bir test dönemindeki başarının farklı zaman dönemlerinde aynı şekilde
devam edip etmeyeceğinin kontrol edilmesi gerektiği sonucuna ulaşıldı.

### Bugün Öğrenilen Kavramlar

- Forecasting
- Train set
- Test set
- Time series train/test split
- Random split ve time-based split farkı
- Baseline model
- Naive forecast
- Scikit-learn
- `sklearn.metrics`
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Absolute error
- `mean_absolute_error()`
- `root_mean_squared_error()`
- `pd.Series()`
- `label`
- `plt.legend()`
- ARIMA
- AutoRegressive (AR)
- Integrated (I)
- Moving Average (MA)
- `ARIMA(p,d,q)`
- Stationarity
- Augmented Dickey-Fuller test
- Null hypothesis
- p-value
- Differencing
- `.diff()`
- Lag
- ACF
- Autocorrelation
- PACF
- Partial autocorrelation
- Confidence interval
- `plot_acf()`
- `plot_pacf()`
- `.fit()`
- `.forecast()`
- `steps`
- Model comparison
- `.sort_values()`
- `.reset_index()`

### Sonraki Adımlar

- Time-series cross-validation mantığını öğrenmek
- Expanding window yöntemi ile modeli birden fazla zaman döneminde test etmek
- ARIMA adaylarının farklı test dönemlerindeki MAE ve RMSE değerlerini
  karşılaştırmak
- Tek test dönemine bağlı model seçimi riskini azaltmak
- Daha güvenilir bir ARIMA modeli belirlemek
- Seçilen model ile gerçek gelecek dönem için forecast üretmek
- Daha sonraki aşamada Prophet modeli ile karşılaştırma yapmak


## Day 5 — 07.08.2026

### Hedefler

- Zaman serisi modellerini tek bir train/test ayrımı yerine birden fazla dönem üzerinde değerlendirmek.
- Projenin yaklaşık 30 günlük tahmin hedefine uygun bir cross-validation yapısı oluşturmak.
- Naive, ARIMA ve Prophet modellerini MAE ve RMSE metrikleriyle karşılaştırmak.
- Prophet modelinin trend değişikliklerine verdiği tepkiyi incelemek ve uygun `changepoint_prior_scale` değerini belirlemek.
- Tahmin ve değerlendirme fonksiyonlarını `src/forecasting.py` altında modüler hale getirmek.

### Yapılan Çalışmalar

#### 1. Time Series Cross-Validation

Zaman serilerinde verilerin sırası korunarak geçmiş verilerle eğitim, sonraki dönemlerle test yapılması için `TimeSeriesSplit` kullanıldı.

İlk olarak:

- 4 fold
- Her fold için 12 haftalık test dönemi

kullanıldı.

ARIMA(1,1,1) için fold sonuçları incelendi ve bazı dönemlerde modelin iyi çalışırken bazı dönemlerde, özellikle ani seviye değişimlerinde, daha yüksek hata yaptığı görüldü.

#### 2. 12 Haftalık Model Karşılaştırması

Naive ve farklı ARIMA modelleri karşılaştırıldı:

- ARIMA(1,1,1)
- ARIMA(0,1,2)
- ARIMA(2,1,0)
- ARIMA(2,1,2)
- Naive

12 haftalık tahminlerde Naive modelin ortalama olarak ARIMA modellerinden daha iyi sonuç verdiği görüldü.

Ancak proje hedefi yaklaşık 30 günlük tahmin olduğu için 12 haftalık horizon yerine daha kısa bir tahmin dönemi kullanılmasına karar verildi.

#### 3. 4 Haftalık Cross-Validation

Haftalık veri kullanıldığı için yaklaşık 30 günlük tahmin hedefi:

- 4 hafta
- yaklaşık 28 gün

olarak ele alındı.

Toplam değerlendirme dönemini korumak amacıyla:

- `n_splits=12`
- `test_size=4`

kullanıldı.

Böylece model 12 farklı dönemde, her seferinde sonraki 4 haftayı tahmin ederek değerlendirildi.

#### 4. Naive ve ARIMA Sonuçları

4 haftalık cross-validation sonucunda:

- ARIMA(1,1,1): MAE ≈ 4.409, RMSE ≈ 4.998
- Naive: MAE ≈ 4.542, RMSE ≈ 5.241

ARIMA(1,1,1), ortalama hata açısından Naive modelden biraz daha iyi performans gösterdi.

Ancak fold bazında incelendiğinde iki modelin de farklı dönemlerde avantajlı olduğu ve ARIMA'nın üstünlüğünün çok büyük olmadığı görüldü.

#### 5. Prophet Modelinin Eklenmesi

Prophet kütüphanesi kuruldu ve model haftalık Google Trends verisine uygulandı.

Prophet için:

- `yearly_seasonality=True`
- `weekly_seasonality=False`
- `daily_seasonality=False`

ayarları kullanıldı.

Prophet'in beklediği veri formatı için:

- tarih sütunu `ds`
- hedef değer `y`

olarak düzenlendi.

#### 6. Prophet 4 Haftalık Cross-Validation

Prophet modeli de aynı 12 fold ve 4 haftalık test yapısıyla değerlendirildi.

Varsayılan:

`changepoint_prior_scale=0.05`

değeriyle Prophet'in ortalama hatasının ARIMA ve Naive modele göre daha yüksek olduğu görüldü.

Bazı foldlarda Prophet çok başarılı olurken bazı foldlarda oldukça yüksek hata yaptı.

#### 7. Prophet Fold Analizi

Özellikle hata oranı yüksek olan Fold 4 ayrıntılı olarak incelendi.

Prophet'in:

- gerçek değerler yaklaşık 75 civarında kalırken
- trend bileşenini yaklaşık 89–92 seviyelerine taşıdığı

görüldü.

Bu durum Prophet'in geçmişteki yükselen trendi geleceğe fazla güçlü şekilde devam ettirdiğini gösterdi.

Modelin hatasının önemli bölümünün yıllık mevsimsellikten değil, trend tahmininden kaynaklandığı görüldü.

#### 8. `changepoint_prior_scale` Kavramı

`changepoint_prior_scale` parametresinin Prophet'in trend değişikliklerine ne kadar esnek tepki vereceğini belirlediği öğrenildi.

Düşük değerlerde model daha düz ve katı bir trend oluştururken, yüksek değerlerde trend değişikliklerine daha fazla izin vermektedir.

Çok yüksek esneklik ise geçmiş verideki küçük hareketlerin gereğinden fazla öğrenilmesine yol açabileceğinden farklı değerlerin cross-validation ile karşılaştırılması gerektiği görüldü.

#### 9. Prophet Hyperparameter Tuning

Farklı `changepoint_prior_scale` değerleri 12 foldun tamamında test edildi.

İlk testlerde:

- 0.01 → MAE ≈ 12.46
- 0.05 → MAE ≈ 6.83
- 0.10 → MAE ≈ 5.92
- 0.20 → MAE ≈ 5.27
- 0.50 → MAE ≈ 4.56
- 1.00 → MAE ≈ 4.30

sonuçları elde edildi.

Daha sonra 1.0 çevresindeki değerler de test edildi.

`1.0` ve `1.25` değerlerinin performanslarının birbirine çok yakın olduğu görüldü.

MAE açısından 1.25 çok küçük bir farkla daha iyi olsa da RMSE açısından 1.0 daha iyi sonuç verdi.

Performans farkı ihmal edilebilir seviyede olduğu için daha sade bir değer olan:

`changepoint_prior_scale=1.0`

seçildi.

#### 10. Nihai Model Karşılaştırması

4 haftalık, 12 fold cross-validation sonucunda:

| Model | MAE | RMSE |
| --- | ---: | ---: |
| Prophet (`cps=1.0`) | 4.303 | 4.826 |
| ARIMA(1,1,1) | 4.409 | 4.998 |
| Naive | 4.542 | 5.241 |

Şu ana kadar test edilen modeller arasında Prophet (`cps=1.0`) en düşük ortalama MAE ve RMSE değerlerini verdi.

Bununla birlikte modeller arasındaki farkın çok büyük olmadığı göz önünde bulunduruldu.

#### 11. Forecasting Modülünün Geliştirilmesi

`src/forecasting.py` içine zaman serisi modelleri için tekrar kullanılabilir fonksiyonlar eklendi.

Modülde:

- `evaluate_naive_cv()`
- `evaluate_arima_cv()`
- `forecast_arima()`
- `evaluate_prophet_cv()`
- `forecast_prophet()`

fonksiyonları oluşturuldu.

Prophet fonksiyonunun notebook içindeki sonuçlarıyla `src` içerisindeki fonksiyonun sonuçlarının aynı olduğu doğrulandı.

`evaluate_prophet_cv()` ile:

- MAE = 4.303037
- RMSE = 4.825669

sonuçları tekrar elde edildi.

#### 12. Güncel Verinin Kontrol Edilmesi

Google Trends verisi güncel tarih aralığıyla tekrar çekildi.

`2026-08-02` haftasının:

`isPartial=True`

olduğu görüldü.

Bu nedenle hafta henüz tamamlanmadığı için bu değer gerçek ve kesin bir gözlem olarak değerlendirmeye dahil edilmedi.

Mevcut son tamamlanmış haftanın verisi kullanılmaya devam edildi.

### Bugün Öğrenilen Kavramlar

- Time Series Cross-Validation
- Expanding Window
- Fold
- Forecast Horizon
- MAE ve RMSE ile model karşılaştırması
- Prophet
- `ds` ve `y` Prophet veri formatı
- Trend ve seasonality bileşenleri
- Changepoint
- `changepoint_prior_scale`
- Hyperparameter tuning
- Overfitting
- Model performansının tek bir test döneminden ziyade birden fazla dönemde değerlendirilmesi
- `isPartial` Google Trends verisinin anlamı
- Tahmin kodlarının modüler fonksiyonlara dönüştürülmesi

### Sonraki Adımlar

- `requirements.txt` dosyasını Prophet kurulumu ile güncellemek.
- README dosyasına Day 5 çalışmalarının kısa özetini eklemek.
- Prophet, ARIMA ve Naive sonuçlarını proje raporu için saklamak.
- Bir sonraki aşamada lag feature'lar oluşturarak makine öğrenmesi tabanlı modelleri değerlendirmek.
- XGBoost/LightGBM sonuçlarını mevcut zaman serisi modelleriyle aynı değerlendirme yöntemi üzerinden karşılaştırmak.

## Day 6 — 10.08.2026

### Hedefler

- XGBoost ile lag tabanlı zaman serisi tahmin modeli oluşturmak.
- Farklı lag uzunluklarını karşılaştırmak.
- Yeni feature'lar ekleyerek model performansını geliştirmek.
- XGBoost hyperparameter tuning yapmak.
- Modeli time-series cross-validation ile değerlendirmek.
- XGBoost evaluation fonksiyonunu `src/forecasting.py` içine taşımak.

### Yapılan Çalışmalar

#### 1. Lag Feature'larının Oluşturulması

ChatGPT Google Trends serisi için önce 4 lag kullanılarak feature set oluşturuldu.

Kullanılan feature'lar:

- `lag_1`
- `lag_2`
- `lag_3`
- `lag_4`

Daha sonra modelin daha uzun geçmişten faydalanıp faydalanmadığını incelemek amacıyla lag sayısı 8'e çıkarıldı.

8 lag kullanıldığında veri seti 149 örneğe düştüğü için 4 lag modeli de aynı 149 tarih aralığına hizalandı. Böylece 4 lag ve 8 lag modelleri aynı eğitim ve test tarihleri üzerinde karşılaştırıldı.

Sonuç:

- 4 Lag MAE ≈ 5.166
- 8 Lag MAE ≈ 4.552

8 haftalık geçmişin model performansını belirgin şekilde iyileştirdiği görüldü.

#### 2. Recursive Forecasting

XGBoost modeli doğrudan zaman bilgisi kullanmadığı için geçmiş değerler lag feature'ları olarak modele verildi.

4 haftalık tahmin horizonunda recursive forecasting kullanıldı.

İlk tahmin gerçek geçmiş değerlerden oluşturulan lag'lerle yapıldı. Sonraki haftaların tahminlerinde ise önceki tahmin değerleri yeni lag olarak kullanıldı.

Bu yöntem sayesinde model gerçek hayatta 4 haftalık ileri tahmin yapılırken oluşacak koşullara benzer şekilde değerlendirildi.

Bazı fold'larda ilk tahmin hatasının sonraki tahminlere aktarılarak error propagation oluşturabileceği gözlemlendi.

#### 3. Fold Bazlı Analiz

12 fold ve her fold için 4 haftalık test horizonuyla `TimeSeriesSplit` kullanıldı.

Özellikle Fold 1, Fold 2 ve Fold 12 detaylı olarak incelendi.

Fold 2'de 8 lag modeli 4 lag modelinden belirgin şekilde daha iyi performans gösterirken, Fold 12'de 4 lag modeli daha başarılı oldu.

Bu durum daha uzun geçmiş bilgisinin her dönemde aynı miktarda fayda sağlamadığını ancak genel ortalamada 8 lag yapısının daha başarılı olduğunu gösterdi.

#### 4. Change Feature'larının Eklenmesi

8 lag modeline yakın dönem yön değişimini daha açık göstermek için iki yeni feature eklendi:

- `change_1 = lag_1 - lag_2`
- `change_2 = lag_2 - lag_3`

Sonuçlar:

- 8 Lag MAE ≈ 4.552
- 8 Lag + Change MAE ≈ 4.536

Change feature'larının küçük fakat olumlu bir katkı sağladığı görüldü.

#### 5. Rolling Mean Denemesi

Son 4 haftanın ortalama seviyesini modele vermek amacıyla `rolling_mean_4` feature'ı test edildi.

Sonuç:

- 8 Lag + Rolling Mean MAE ≈ 4.578

Rolling mean feature'ı MAE açısından iyileşme sağlamadı. Bu nedenle final feature setine dahil edilmedi.

#### 6. max_depth Tuning

8 Lag + Change yapısı sabit tutularak farklı `max_depth` değerleri karşılaştırıldı.

Sonuçlar:

- `max_depth = 2` → MAE ≈ 4.472
- `max_depth = 3` → MAE ≈ 4.536
- `max_depth = 4` → MAE ≈ 5.467
- `max_depth = 5` → MAE ≈ 5.620

En iyi sonuç `max_depth = 2` ile elde edildi.

Daha derin ağaçların küçük veri setinde gereğinden fazla karmaşık modeller oluşturabileceği ve generalization performansını düşürebileceği gözlemlendi.

#### 7. n_estimators Tuning

`max_depth = 2` ve `learning_rate = 0.05` sabit tutularak farklı ağaç sayıları test edildi.

Sonuçlar:

- 50 estimators → MAE ≈ 5.647
- 100 estimators → MAE ≈ 4.472
- 200 estimators → MAE ≈ 4.401
- 300 estimators → MAE ≈ 4.430

Bu aşamada en iyi sonuç `n_estimators = 200` ile elde edildi.

#### 8. learning_rate Tuning

`max_depth = 2` ve `n_estimators = 200` sabit tutularak farklı learning rate değerleri karşılaştırıldı.

En iyi sonuç `learning_rate = 0.05` ile elde edildi.

Daha küçük `learning_rate` değerlerinde 200 ağacın yeterli olmayabileceği, daha yüksek değerlerde ise model performansının bozulduğu gözlemlendi.

#### 9. Final Hyperparameter Grid

`learning_rate` ve `n_estimators` parametrelerinin birbirleriyle ilişkili olması nedeniyle küçük bir final grid denemesi yapıldı.

Test edilen kombinasyonlar:

- `learning_rate`: 0.03, 0.05, 0.10
- `n_estimators`: 100, 200, 300
- `max_depth`: 2

En iyi kombinasyon:

- `n_estimators = 300`
- `max_depth = 2`
- `learning_rate = 0.03`

Final XGBoost sonucu:

- MAE ≈ 4.356
- RMSE ≈ 4.902

#### 10. Final XGBoost Yapısı

Final feature seti:

- `lag_1` ... `lag_8`
- `change_1`
- `change_2`



#### 11. Modelin Modüler Hale Getirilmesi

Notebook içinde geliştirilen recursive XGBoost evaluation fonksiyonu `src/forecasting.py` dosyasına taşındı.

Yeni fonksiyon:

`evaluate_xgb_recursive_with_change()`

Fonksiyon içerisinde:

* XGBoost modelinin eğitilmesi,
* recursive forecast oluşturulması,
* MAE hesaplanması,
* RMSE hesaplanması,
* fold sonuçlarının DataFrame olarak döndürülmesi

işlemleri tek bir yapı altında toplandı.



### Bugün Öğrenilen Kavramlar

* Lag feature
* Recursive forecasting
* Error propagation
* Feature engineering
* Change feature
* Rolling mean
* XGBoost decision trees
* Boosting
* `n_estimators`
* `max_depth`
* `learning_rate`


* Overfitting
* Hyperparameter tuning
* Controlled experiment
* Time-series cross-validation
* Fold bazlı model analizi
* Model fonksiyonlarının modülerleştirilmesi


### Sonraki Adımlar

* Naive, ARIMA, Prophet ve tuned XGBoost modellerini tamamen aynı tarih aralığında yeniden değerlendirmek.
* Modelleri aynı 12 fold $\times$ 4 haftalık test yapısında karşılaştırmak.
* Final ChatGPT model karşılaştırma tablosunu oluşturmak.
* Daha sonra aynı pipeline'ı Gemini ve Claude trend serileri üzerinde çalıştırmak.

## Day 7 — 11.08.2026

### Hedefler

- Tüm modelleri aynı tarih aralığında yeniden değerlendirmek.
- Naive, ARIMA, Prophet ve XGBoost modellerini adil şekilde karşılaştırmak.
- Modellerin yalnızca ortalama hata değerlerine değil, fold bazlı davranışlarına da bakmak.
- Prophet ve XGBoost modellerinin birlikte kullanıldığı bir ensemble modeli denemek.
- Ensemble ağırlıklarının performansa etkisini incelemek.

### Yapılan Çalışmalar

#### 1. Verilerin Aynı Tarih Aralığına Hizalanması

XGBoost modeli 8 lag kullandığı için ilk 8 haftada gerekli feature'lar
oluşturulamamaktadır.

Bu nedenle 157 haftalık ChatGPT trend serisinin ilk 8 haftası çıkarılarak tüm
modeller aynı 149 haftalık dönem üzerinde değerlendirilmiştir.

Hizalanmış veri aralığı:

- Başlangıç: 2023-09-24
- Bitiş: 2026-07-26
- Toplam gözlem: 149

Cross-validation yapısı:

- `n_splits = 12`
- `test_size = 4`

Böylece son 48 haftayı kapsayan 12 farklı yaklaşık 1 aylık tahmin dönemi
değerlendirilmiştir.

#### 2. Modellerin Yeniden Değerlendirilmesi

Tüm modeller aynı veri aralığı ve aynı cross-validation yapısında tekrar
çalıştırılmıştır.

Sonuçlar:

| Model | MAE | RMSE |
| --- | ---: | ---: |
| Naive | 4.542 | 5.241 |
| ARIMA(1,1,1) | 4.414 | 5.000 |
| Prophet (`cps=1.0`) | 4.211 | 4.745 |
| Tuned XGBoost | 4.356 | 4.902 |

Tek başına kullanılan modeller arasında Prophet en düşük ortalama MAE ve RMSE
değerlerini elde etmiştir.

#### 3. Fold Bazlı Model Analizi

Modellerin her fold'daki MAE değerleri karşılaştırılmıştır.

İlk karşılaştırmada:

- XGBoost 6 fold'da en iyi sonucu vermiştir.
- Prophet 3 fold'da en iyi sonucu vermiştir.
- Naive 3 fold'da en iyi sonucu vermiştir.
- ARIMA hiçbir fold'da doğrudan birinci olmamıştır.

Buna rağmen Prophet'in ortalama MAE değeri XGBoost'tan daha düşüktür.

Bu durum XGBoost'un birçok dönemde çok başarılı olmasına rağmen bazı dönemlerde
daha büyük hatalar yapmasından kaynaklanmaktadır.

Fold MAE istatistikleri incelendiğinde:

- Prophet MAE standart sapması ≈ 2.814
- XGBoost MAE standart sapması ≈ 3.544

En kötü fold MAE değerleri:

- Prophet ≈ 8.965
- XGBoost ≈ 11.560

Medyan MAE değerleri:

- XGBoost ≈ 3.547
- Prophet ≈ 3.658

Bu sonuçlar XGBoost'un tipik dönemlerde çok güçlü olduğunu ancak performansının
dönemler arasında daha fazla değiştiğini göstermiştir.

Prophet ise daha düşük ortalama hata ve daha kontrollü en kötü durum
performansı göstermiştir.

#### 4. Prophet + XGBoost Ensemble Modeli

Prophet ve XGBoost tahminlerinin birbirlerinin hatalarını dengeleyip
dengeleyemeyeceğini görmek amacıyla eşit ağırlıklı bir ensemble oluşturulmuştur.

Kullanılan formül:

`Ensemble Prediction = 0.5 × Prophet Prediction + 0.5 × XGBoost Prediction`

Ensemble modeli aynı 12-fold ve 4 haftalık cross-validation yapısında
değerlendirilmiştir.

Sonuç:

- MAE ≈ 3.911
- RMSE ≈ 4.520
- Median MAE ≈ 2.342
- Worst Fold MAE ≈ 8.688
- Fold MAE Std ≈ 2.928

Ensemble modeli ortalama MAE ve RMSE açısından tüm tekil modellerden daha iyi
performans göstermiştir.

Ensemble her fold'da doğrudan en iyi model olmamasına rağmen Prophet ve
XGBoost'un bazı dönemlerde farklı yönlerde hata yapması sayesinde tahminlerin
ortalaması gerçek değerlere daha fazla yaklaşmıştır.

#### 5. Ensemble Weight Sensitivity

Ensemble'ın belirli bir ağırlık kombinasyonuna aşırı bağımlı olup olmadığını
görmek için birkaç farklı Prophet/XGBoost ağırlığı test edilmiştir.

| Prophet Weight | XGBoost Weight | MAE | RMSE |
| ---: | ---: | ---: | ---: |
| 0.5 | 0.5 | 3.911 | 4.520 |
| 0.4 | 0.6 | 3.918 | 4.555 |
| 0.6 | 0.4 | 3.930 | 4.507 |
| 0.7 | 0.3 | 3.968 | 4.525 |

`0.6 / 0.4` kombinasyonu RMSE açısından çok az daha iyi sonuç vermiştir.

Ancak `0.5 / 0.5` kombinasyonu:

- En düşük MAE değerini vermiştir.
- RMSE açısından en iyi sonuca çok yakın kalmıştır.
- Daha basit ve yorumlanabilir bir yapı sunmaktadır.

Bu nedenle final ensemble adayı olarak eşit ağırlıklı `0.5 / 0.5`
kombinasyonunda kalınmıştır.

### Bugün Öğrenilen Kavramlar

- Modelleri adil karşılaştırmak için aynı tarih aralığı ve aynı test dönemlerinin
  kullanılması gerektiği.
- Fold sayısının fazla olmasının her zaman daha iyi değerlendirme anlamına
  gelmediği.
- Bir modelin daha fazla fold kazanmasının ortalama olarak en iyi model olduğu
  anlamına gelmediği.
- Ortalama MAE'nin tüm dönemlerdeki genel hata seviyesini gösterdiği.
- Medyan MAE'nin modelin daha tipik dönemlerdeki davranışı hakkında bilgi verdiği.
- Standart sapmanın model performansının dönemler arasında ne kadar değiştiğini
  gösterdiği.
- Worst Fold MAE'nin modelin kötü bir dönemde ne kadar sapabileceğini
  değerlendirmeye yardımcı olduğu.
- Ensemble modellerde hata değerlerinin değil, doğrudan model tahminlerinin
  birleştirildiği.
- İki model farklı yönlerde hata yaptığında tahmin ortalamasının gerçek değere
  daha fazla yaklaşabileceği.
- Ensemble ağırlıklarının küçük bir aralıkta test edilerek modelin ağırlıklara
  karşı hassasiyetinin incelenebileceği.

### Sonraki Adımlar

- Aynı modelleme ve değerlendirme pipeline'ını Gemini trend serisine uygulamak.
- Naive, ARIMA, Prophet, XGBoost ve ensemble modellerini Gemini üzerinde
  karşılaştırmak.
- Gerekirse Gemini serisi için model parametrelerinin yeniden ayarlanmasını
  değerlendirmek.
- Daha sonra aynı analizi Claude trend serisine uygulamak.
- Farklı trend serilerinde aynı modelin mi yoksa farklı modellerin mi daha iyi
  çalıştığını karşılaştırmak.


## Day 8 — 12.08.2026

### Hedefler

- Gemini ve Claude trend serilerindeki model karşılaştırmalarını tamamlamak.
- ChatGPT, Gemini ve Claude sonuçlarını ortak bir tabloda değerlendirmek.
- Her trend serisi için en başarılı modeli otomatik seçebilen bir yapı oluşturmak.
- Seçilen modellerle ileriye dönük 4 haftalık tahmin üretmek.
- Ani dış olayların tahmin modellerine nasıl dahil edilebileceğini değerlendirmek.

### Yapılan Çalışmalar

#### 1. Gemini Model Analizi Tamamlandı

Gemini trend serisi Naive, ARIMA, Prophet, XGBoost ve Ensemble modelleri ile aynı time-series cross-validation yapısı altında değerlendirildi.

Gemini serisinde özellikle 2025 Ağustos sonu ve Eylül ayında çok büyük bir trend artışı olduğu görüldü. Araştırma sonucunda bu artışın zamanlamasının Gemini 2.5 Flash Image / Nano Banana ürününün yayınlanması ve viral hale gelmesi ile güçlü biçimde örtüştüğü görüldü.

Bu örnek üzerinden geçmiş trend değerlerini kullanan modellerin, veri içerisinde daha önce işaret bulunmayan dışsal olayları önceden tahmin etmekte zorlanabileceği gözlemlendi.

Gemini için en başarılı model:

- ARIMA Mean MAE: yaklaşık 6.582

oldu.

#### 2. Claude Model Karşılaştırması Yapıldı

Claude trend serisi aynı 12-fold ve 4 haftalık test yapısı kullanılarak değerlendirildi.

Elde edilen Mean MAE sonuçları:

- ARIMA: 1.317
- Prophet: 1.415
- Naive: 1.438
- Ensemble: 1.492
- XGBoost: 1.701

Genel hata açısından ARIMA en başarılı model oldu.

Fold bazında ise en fazla kazanan model Naive oldu:

- Naive: 6 fold
- ARIMA: 2 fold
- XGBoost: 2 fold
- Prophet: 1 fold
- Ensemble: 1 fold

Bu analiz sonucunda yalnızca kaç fold kazanıldığına bakmanın yeterli olmadığı; Mean MAE, Median MAE, RMSE ve hata dağılımının birlikte değerlendirilmesi gerektiği görüldü.

#### 3. Prophet Ayarları Standartlaştırıldı

Gemini analizinde Prophet'in `yearly_seasonality=True` ve `"auto"` ayarları arasında bazı fold'larda büyük performans farkı oluştuğu görüldü.

Final model karşılaştırmasında daha tutarlı bir yapı oluşturmak amacıyla Prophet değerlendirmeleri `yearly_seasonality="auto"` kullanılarak standartlaştırıldı.

ChatGPT için Prophet'in yeni Mean MAE değeri:

- Prophet: 4.235

olarak elde edildi.

#### 4. Üç Trend Serisinin Final Model Karşılaştırması Yapıldı

ChatGPT, Gemini ve Claude serileri aynı değerlendirme sistemi altında karşılaştırıldı.

Final Mean MAE sonuçlarına göre:

| Trend | En İyi Yöntem | Mean MAE |
|---|---|---:|
| ChatGPT | Ensemble | 3.911 |
| Gemini | ARIMA | 6.582 |
| Claude | ARIMA | 1.317 |

ChatGPT serisinde en başarılı tekil model Prophet olsa da Prophet ve XGBoost tahminlerinin %50-%50 birleştirildiği Ensemble yaklaşımı genel olarak daha düşük hata verdi.

Bu sonuç, tek bir forecasting modelinin bütün trend serileri için en iyi seçenek olmadığını gösterdi.

#### 5. Otomatik Model Seçim Fonksiyonu Geliştirildi

`src/forecasting.py` dosyasına `select_best_model()` fonksiyonu eklendi.

Fonksiyon:

1. Modellerin cross-validation sonuçlarını alıyor.
2. Her model için Mean MAE ve Mean RMSE hesaplıyor.
3. Sonuçları Mean MAE değerine göre sıralıyor.
4. En düşük Mean MAE değerine sahip modeli otomatik olarak seçiyor.

ChatGPT üzerinde yapılan test sonucunda fonksiyon doğru şekilde:

`Best model: Ensemble`

sonucunu verdi.

Aynı sistem Gemini ve Claude gibi farklı trend serilerine de uygulanabilecek şekilde oluşturuldu.

#### 6. ARIMA ile Final Gelecek Tahminleri Üretildi

Cross-validation sonrasında seçilen modeller artık geçmiş test dönemleri yerine mevcut tüm veri kullanılarak ileriye dönük tahmin üretmek için kullanıldı.

Gemini için ARIMA tahmini yaklaşık olarak:

- 2026-08-02: 37.82
- 2026-08-09: 37.85
- 2026-08-16: 37.85
- 2026-08-23: 37.85

Claude için ARIMA tahmini yaklaşık olarak:

- 2026-08-02: 16.00
- 2026-08-09: 16.00
- 2026-08-16: 16.00
- 2026-08-23: 16.00

şeklinde gerçekleşti.

Her iki model de mevcut veriye göre yakın dönemde büyük bir değişim öngörmedi.

#### 7. XGBoost İçin Recursive Future Forecast Fonksiyonu Eklendi

Cross-validation sırasında kullanılan recursive XGBoost mantığının gerçek geleceğe tahmin üretebilmesi için yeni bir fonksiyon geliştirildi:

`forecast_xgb_recursive_with_change()`

Fonksiyon:

- son 8 haftalık lag değerlerini,
- `change_1`,
- `change_2`

özelliklerini kullanıyor.

Her yeni tahmin bir sonraki haftanın lag değerleri arasına eklenerek recursive şekilde sonraki tahmin üretiliyor.

ChatGPT için elde edilen XGBoost tahminleri yaklaşık olarak:

- 67.73
- 69.41
- 70.82
- 71.22

oldu.

#### 8. ChatGPT Final Ensemble Forecast Oluşturuldu

ChatGPT için Prophet ve XGBoost modellerinin gelecek 4 haftalık tahminleri ayrı ayrı üretildi.

Final tahmin:

`0.5 × Prophet + 0.5 × XGBoost`

formülü ile oluşturuldu.

Yaklaşık Ensemble tahminleri:

- 2026-08-02: 67.18
- 2026-08-09: 67.98
- 2026-08-16: 69.11
- 2026-08-23: 70.09

oldu.

Model, ChatGPT Google Trends ilgisinde hafif yükselen bir hareket öngördü.

#### 9. Final Forecast Tablosu Oluşturuldu

ChatGPT, Gemini ve Claude için seçilen final modellerin tahminleri tek bir DataFrame içerisinde birleştirildi.

Final yapı:

- ChatGPT → Ensemble
- Gemini → ARIMA
- Claude → ARIMA

şeklinde oluşturuldu.

Forecast CSV dosyalarının hangi veri tarihine dayanarak üretildiğinin anlaşılabilmesi için dosya isimlerinde son gözlem tarihi kullanılmasına karar verildi.

Örnek:

`final_forecast_as_of_2026-07-26.csv`

### Bugün Öğrenilen Kavramlar

- Bir modelin en fazla fold'u kazanması, genel olarak en iyi model olduğu anlamına gelmeyebilir.
- Mean MAE, Median MAE, RMSE ve standart sapma farklı performans özelliklerini gösterir.
- Tek bir forecasting modeli bütün zaman serilerinde en iyi sonucu vermeyebilir.
- Model seçimi cross-validation performansına göre otomatikleştirilebilir.
- Cross-validation geçmişteki performansı ölçerken final forecast mevcut tüm veri kullanılarak geleceğe tahmin üretir.
- Recursive forecasting sırasında önceki tahminler sonraki tahminlerin girdisi haline gelir.
- Dış dünyadaki ani ürün lansmanları veya viral olaylar yalnızca geçmiş trend değerlerini kullanan modeller tarafından önceden görülemeyebilir.
- Bilinen ürün lansmanları, haberler veya diğer dış sinyaller gelecekte external/exogenous feature olarak modele eklenebilir.
- Tahmin sırasında henüz bilinmeyen bir bilginin geçmiş test verisine eklenmesi data leakage oluşturur.
- Forecast dosyasının veri kesim tarihini dosya adında tutmak farklı tahmin versiyonlarının takip edilmesini kolaylaştırır.

### Sonraki Adımlar

- Google Trends verisini güncelleyerek en güncel haftaları veri setine eklemek.
- Final forecasting pipeline'ını daha modüler hale getirmek.
- Seçilen modellerin final çıktılarının kaydedilmesini düzenlemek.
- Gerekli model nesnelerini `.pkl` formatında kaydetmek.
- Event-aware forecasting yaklaşımını Gemini / Nano Banana örneği üzerinde kontrollü bir deney olarak test etmek.
- Event-aware geliştirmeden sonra dashboard ve erken uyarı mekanizmasına geçmek.
- README, requirements ve GitHub repo içeriğini güncellemek.
