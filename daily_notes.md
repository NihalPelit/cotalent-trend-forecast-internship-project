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
