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

## Day 9 — 13.08.2026

### Hedefler

- Google Trends verisini yeni haftalarla güncellemek
- Önceki gün üretilen tahminleri yeni gerçekleşen verilerle doğrulamak
- Güncel veriyle modelleri yeniden değerlendirmek
- Google Trends'in doğal 0–100 sınırını model değerlendirmesine dahil etmek
- Her trend için güncel en iyi modeli yeniden seçmek
- Yeni 4 haftalık tahminleri üretmek
- Anomaly detection için ilk prototipi oluşturmak


### Yapılan Çalışmalar

#### 1. Google Trends Verisinin Güncellenmesi

Pytrends üzerinden yeni veri çekilmeye çalışıldı ancak istek sırasında `ResponseError: 400` hatası alındı.

Bu nedenle Google Trends web arayüzünden manuel olarak son 1 yıllık haftalık veri indirildi.

Eski 3 yıllık veri ile yeni indirilen veri arasında ortak tarihler karşılaştırıldı. Aynı tarihlerde küçük değer farklılıkları bulundu.

51 haftalık overlap üzerinde:

- ChatGPT için median scale ratio yaklaşık `1.016`
- Gemini için median scale ratio `1.0`
- Claude için median scale ratio `1.0`
- Tüm seriler için global median scale ratio `1.0`

olarak bulundu.

Global scaling uygulandığında ChatGPT farkı azalırken Gemini ve Claude için farkın arttığı görüldü.

Bu nedenle geçmiş veriyi yeniden ölçeklemek yerine yalnızca yeni haftaların eklenmesine karar verildi.

Yeni eklenen haftalar:

- 2026-08-02
- 2026-08-09

Güncellenmiş veri seti 157 satırdan 159 satıra çıktı.


#### 2. Önceki Tahminlerin Gerçek Verilerle Doğrulanması

Day 8 sonunda 2026-07-26 tarihi itibarıyla üretilen tahminler ile yeni gerçekleşen iki haftalık veriler karşılaştırıldı.

İlk iki haftalık gerçek future validation sonucunda yaklaşık MAE değerleri:

- ChatGPT: `1.598`
- Gemini: `2.163`
- Claude: `1.499`

olarak bulundu.

ChatGPT tahmini yükseliş yönünü doğru yakaladı ancak ikinci haftadaki gerçek değerin biraz altında kaldı.

Gemini tahmini yatay seyri doğru yakaladı ancak gerçek seviyenin biraz altında kaldı.

Claude tahmini ise gerçekleşen değerlere oldukça yakın kaldı.

Bu değerlendirme yalnızca iki haftalık gerçek gelecek verisini içerdiği için sonuçların henüz sınırlı olduğu not edildi.


#### 3. Güncel Veriyle Modellerin Yeniden Değerlendirilmesi

Güncellenmiş veri kullanılarak aynı cross-validation yapısı tekrar çalıştırıldı:

- `TimeSeriesSplit`
- 12 fold
- Her fold için 4 haftalık test dönemi
- Expanding training window

ChatGPT, Gemini ve Claude için aşağıdaki modeller yeniden değerlendirildi:

- Naive
- ARIMA
- Prophet
- XGBoost
- Prophet + XGBoost Ensemble


#### 4. Gemini ARIMA Fold 1 Probleminin İncelenmesi

Gemini için güncel ARIMA sonucunda Mean MAE değerinin yaklaşık `10.97` seviyesine yükselmesi dikkat çekti.

Fold bazında inceleme yapıldığında problemin büyük ölçüde Fold 1'den kaynaklandığı görüldü.

Fold 1 tahminleri:

| Date | Actual | ARIMA |
|---|---:|---:|
| 2025-09-14 | 100 | 104.15 |
| 2025-09-21 | 60 | 144.57 |
| 2025-09-28 | 45 | 184.27 |
| 2025-10-05 | 37 | 223.27 |

ARIMA, eğitim verisinin sonunda görülen hızlı yükselişi geleceğe taşımaya devam ederken gerçek seri zirveden sonra düşüşe geçti.

Google Trends değerlerinin doğal olarak `0–100` arasında olmasına rağmen ARIMA modelinin böyle bir sınırı olmadığı için 100'ün üzerinde tahminler üretebildiği görüldü.


#### 5. Bounded Forecast Yaklaşımının Eklenmesi

Google Trends skorlarının doğal veri aralığı dikkate alınarak tahminler için:

`0 <= prediction <= 100`

sınırı uygulanmaya başlandı.

ARIMA Fold 1 sonucu:

- Original MAE: `103.566`
- Clipped MAE: `39.500`

Tüm Gemini cross-validation sonuçlarında:

- Normal ARIMA MAE: `10.974`
- Clipped ARIMA MAE: `5.635`
- Clipped ARIMA RMSE: `6.494`

olarak bulundu.

Clipping, gerçek dışı extrapolation problemini ciddi biçimde azalttı ancak trend dönüşünü tahmin edememe problemini tamamen çözmedi.

Daha sonra aynı 0–100 sınırı Prophet, XGBoost ve Ensemble değerlendirmelerine de eklendi.


#### 6. Güncel Model Seçimi

Bounded değerlendirme sonrasında modeller yeniden karşılaştırıldı.

##### ChatGPT

| Model | Mean MAE |
|---|---:|
| Ensemble | 3.850 |
| XGBoost | 3.856 |
| Prophet | 4.563 |
| ARIMA | 4.872 |
| Naive | 5.167 |

Seçilen model:

**Ensemble (Prophet + XGBoost)**


##### Gemini

| Model | Mean MAE |
|---|---:|
| Naive | 4.333 |
| ARIMA Clipped | 5.635 |
| Ensemble Clipped | 6.890 |
| XGBoost Clipped | 8.278 |
| Prophet Clipped | 8.315 |

Seçilen model:

**Naive**


##### Claude

| Model | Mean MAE |
|---|---:|
| Naive | 1.583 |
| ARIMA | 1.645 |
| Ensemble | 1.809 |
| Prophet | 1.820 |
| XGBoost | 2.005 |

Seçilen model:

**Naive**

Bu sonuç, her trend serisi için aynı modelin kullanılmasının gerekli olmadığını gösterdi.


#### 7. Güncellenmiş 4 Haftalık Forecast

Yeni veri ve güncel model seçimleri kullanılarak 4 haftalık tahmin üretildi.

| Date | ChatGPT | Gemini | Claude |
|---|---:|---:|---:|
| 2026-08-16 | 70.25 | 40 | 15 |
| 2026-08-23 | 70.85 | 40 | 15 |
| 2026-08-30 | 71.37 | 40 | 15 |
| 2026-09-06 | 72.02 | 40 | 15 |

ChatGPT için Ensemble modeli hafif yükseliş öngördü.

Gemini ve Claude için seçilen Naive modelleri son gözlenen değerin gelecek haftalarda korunacağını tahmin etti.


#### 8. Anomaly Detection Prototipi

Tahmin sistemine ek olarak ani trend değişimlerini tespit etmek amacıyla ilk anomaly detection prototipi oluşturuldu.

Gemini serisi üzerinde:

- 8 haftalık rolling mean
- 8 haftalık rolling standard deviation
- anomaly score

hesaplandı.

Anomaly score mantığı:

`(Current Value - Rolling Mean) / Rolling Standard Deviation`

şeklinde kuruldu.

Amaç, mevcut haftanın yakın geçmişteki normal davranıştan ne kadar uzak olduğunu ölçmekti.

Gemini'nin 2025 Ağustos–Eylül dönemindeki ani yükselişi güçlü biçimde tespit edildi.

Özellikle:

- 2025-08-31: anomaly score `15.67`
- 2025-09-07: anomaly score `8.32`
- 2025-09-14: anomaly score `4.37`

olarak bulundu.

Bu dönem, Gemini trendindeki büyük spike'ın başladığı dönemle örtüştü.


#### 9. Anomaly Detection İçin İlk İyileştirme

Tüm veri üzerinde anomaly noktaları görüntülendiğinde bazı eski dönemlerde `inf` değerleri görüldü.

Bunun sebebi, bazı 8 haftalık dönemlerde rolling standard deviation değerinin `0` olmasıydı.

Sıfıra bölme problemini önlemek ve küçük değer değişimlerinin gereksiz alarm üretmesini azaltmak için daha güvenli bir yapı oluşturuldu:

- `WINDOW = 8`
- `ANOMALY_THRESHOLD = 3`
- `MIN_ABSOLUTE_CHANGE = 5`

Standart sapmanın 0 olduğu durumlar ayrıca ele alındı.

Bu değerlerin henüz final parametreler olmadığı ve sonraki çalışmalarda farklı window ve threshold değerlerinin karşılaştırılması gerektiği not edildi.


### Bugün Öğrenilen Kavramlar

- Yeni veri geldiğinde model performansının değişebileceği
- Cross-validation fold sınırlarının yeni veri geldikçe kayabileceği
- Tek bir ekstrem fold'un Mean MAE değerini ciddi biçimde etkileyebileceği
- Tahmin modellerinde domain bilgisinin önemli olduğu
- Google Trends için 0–100 prediction constraint uygulanması
- Clipping'in gerçek dışı extrapolation'ı sınırlandırması
- Basit modellerin bazı serilerde karmaşık modellerden daha dayanıklı olabileceği
- Gerçek future validation ile cross-validation arasındaki fark
- Rolling mean ve rolling standard deviation
- Z-score tabanlı anomaly detection
- Anomaly threshold kavramı
- Sıfır standard deviation nedeniyle oluşan `inf` problemi
- False alarm azaltmak için minimum absolute change kullanımı
- Forecasting ile anomaly detection'ın farklı ama tamamlayıcı görevler olduğu


### Sonraki Adımlar

- Anomaly detection için farklı window değerlerini karşılaştırmak
- Anomaly threshold değerini veri üzerinden daha sistematik belirlemek
- False positive / false negative örneklerini incelemek
- Anomaly noktalarını grafik üzerinde göstermek
- Trend spike algılandığında erken uyarı mekanizması oluşturmak
- Event-aware forecasting yaklaşımını Gemini örneği üzerinde test etmek
- Bilinen ürün lansmanı / duyuru gibi dış olayları feature olarak eklemeyi araştırmak
- Final forecasting fonksiyonlarında 0–100 sınırını pipeline seviyesinde standartlaştırmak
- Dashboard aşamasında forecast ve anomaly bilgilerini birlikte göstermek

## Day 10 — 14.08.2026

### Hedefler

- Anomaly detection prototipini geliştirmek
- Rolling window, anomaly threshold ve minimum değişim parametrelerini karşılaştırmak
- Anomaly noktalarını görselleştirmek
- ChatGPT, Gemini ve Claude için güncel monitoring sistemi oluşturmak
- Event-aware forecasting yaklaşımını deneysel olarak test etmek
- Event feature'larının XGBoost performansına katkı sağlayıp sağlamadığını incelemek


### Yapılan Çalışmalar

#### 1. Anomaly Detection Fonksiyonunun Oluşturulması

Gemini Google Trends serisinde olağan dışı hareketleri tespit etmek amacıyla
tekrar kullanılabilir `detect_anomalies()` fonksiyonu oluşturuldu.

Fonksiyon içerisinde:

- Rolling mean
- Rolling standard deviation
- Absolute change
- Anomaly score
- Anomaly flag

hesaplandı.

Anomaly score, mevcut değerin yakın geçmişteki normal davranıştan kaç standart
sapma uzaklaştığını ölçmek için kullanıldı.


#### 2. Rolling Window Karşılaştırması

Anomaly detection için farklı geçmiş pencere uzunlukları test edildi:

- `window=4`
- `window=8`
- `window=12`

Sonuçlar:

- `window=4` → 2 anomaly
- `window=8` → 5 anomaly
- `window=12` → 4 anomaly

Bilinen Gemini sıçrama döneminde:

- 2025-08-31 → 28
- 2025-09-07 → 63
- 2025-09-14 → 100

haftalarının tamamını 8 ve 12 haftalık pencereler yakaladı.

4 haftalık pencerenin yeni yüksek değerlere hızlı adapte olarak son spike haftasını
kaçırdığı görüldü.

12 haftalık pencere büyük sıçramanın tamamını yakalarken 8 haftalık pencereye
göre daha az ek alarm üretti.

Bu nedenle mevcut prototip için:

`window = 12`

seçildi.


#### 3. Anomaly Threshold Karşılaştırması

`window=12` sabit tutularak farklı threshold değerleri test edildi.

Sonuçlar:

- `threshold=2.0` → 8 anomaly
- `threshold=2.5` → 6 anomaly
- `threshold=3.0` → 4 anomaly
- `threshold=3.5` → 3 anomaly

`threshold=3.5`, bilinen üç büyük Gemini spike haftasının tamamını tespit etti
ve bu karşılaştırmada ek alarm üretmedi.

Bu nedenle mevcut prototip için:

`threshold = 3.5`

seçildi.


#### 4. Minimum Absolute Change Karşılaştırması

Minimum gerçek değişim şartı için:

- `0`
- `3`
- `5`
- `10`

değerleri karşılaştırıldı.

Sonuçlar:

- `0` → 12 anomaly
- `3` → 3 anomaly
- `5` → 3 anomaly
- `10` → 3 anomaly

Minimum değişim şartı kaldırıldığında özellikle standart sapmanın sıfır olduğu
dönemlerde gereksiz alarmlar oluşabildiği görüldü.

`3`, `5` ve `10` mevcut Gemini spike'ları için aynı sonucu verdi.

Çok düşük veya çok yüksek bir sınır kullanmamak amacıyla mevcut prototipte:

`min_absolute_change = 5`

korundu.


#### 5. Final Anomaly Detection Parametreleri

Mevcut prototip için seçilen parametreler:

- `window = 12`
- `threshold = 3.5`
- `min_absolute_change = 5`

Bu değerlerin kesin optimum parametreler olmadığı ve daha fazla gerçek event
incelendikçe yeniden değerlendirilebileceği not edildi.


#### 6. Gemini Anomaly Detection Görselleştirmesi

Gemini zaman serisi üzerinde:

- gerçek Google Trends serisi
- 12 haftalık rolling mean
- anomaly noktaları

aynı grafikte gösterildi.

Detector özellikle:

- 2025-08-31
- 2025-09-07
- 2025-09-14

tarihlerindeki büyük Gemini trend sıçramasını doğru şekilde işaretledi.


#### 7. Anomaly Detection'ın Diğer Trendlere Uygulanması

Aynı anomaly detection prototipi ChatGPT ve Claude serilerine de uygulandı.

Tespit edilen anomaly sayıları:

- ChatGPT → 3
- Gemini → 3
- Claude → 1

ChatGPT'de hem yukarı hem aşağı yönlü sıra dışı hareketler tespit edildi.

Claude için 2026-03-01 tarihinde yukarı yönlü bir anomaly bulundu.

Aynı parametrelerin farklı serilerde aşırı sayıda alarm üretmediği gözlemlendi,
ancak parametrelerin bütün trendler için kesin optimum olduğu sonucuna varılmadı.


#### 8. Anomaly Event Validation

Anomaly tarihleri dış gelişmelerle karşılaştırıldı.

Bazı anomaly dönemlerinin ürün lansmanları ve yoğun haber dönemleriyle zaman
olarak örtüştüğü görüldü.

Özellikle ChatGPT'nin 2025-03-30 tarihindeki güçlü pozitif anomaly'si,
GPT-4o image generation lansmanı ve takip eden viral kullanım dönemiyle
yakın zamanlı bulundu.

Negatif Christmas dönemi anomaly'lerinde ise olası holiday seasonality etkisi
değerlendirildi.

Anomaly detection'ın olayların nedenini kanıtlamadığı; yalnızca analistin
araştırması gereken sıra dışı tarihleri belirlediği vurgulandı.


#### 9. Güncel Early-Warning ve Monitoring Sistemi

ChatGPT, Gemini ve Claude için en güncel hafta tek tabloda özetlendi.

2026-08-09 itibarıyla:

- ChatGPT → Anomaly Score ≈ `0.47`
- Gemini → Anomaly Score ≈ `-0.54`
- Claude → Anomaly Score ≈ `-1.26`

Üç trend için de `Is_Anomaly=False` sonucu elde edildi.

Böylece güncel haftada güçlü ve olağan dışı bir trend hareketi tespit edilmedi.

Bu yapı ileride Streamlit dashboard üzerinde early-warning sistemi olarak
kullanılabilecek bir monitoring çıktısı oluşturdu.


#### 10. Event-Aware Forecasting Deneyi

Gemini için tarihsel önemli ürün ve model duyurularından oluşan event catalog
oluşturuldu.

Event tarihleri haftalık Google Trends gözlemleriyle eşleştirildi.

Aşağıdaki event feature'ları üzerinde çalışıldı:

- `event_occurred`
- `event_count`
- `event_occurred_lag_1`
- `event_recent_4w`
- `event_count_recent_4w`

Data leakage oluşmaması için henüz gerçekleşmemiş event bilgilerinin geçmiş
tahminlerde kullanılmamasına dikkat edildi.


#### 11. Baseline vs Event-Aware XGBoost

Event feature'larının forecasting performansına etkisini test etmek için
1 haftalık walk-forward evaluation oluşturuldu.

Baseline model:

`lag_1 ... lag_8 + change_1 + change_2`

Event-Aware model:

Baseline feature'ları + `event_recent_4w`

Genel sonuçlar:

- Baseline MAE: `3.087`
- Event-Aware MAE: `3.064`

İlk bakışta Event-Aware model çok küçük bir iyileşme gösterdi.


#### 12. Event ve Normal Dönemlerin Ayrı Analizi

Event dönemleri ayrıca değerlendirildi.

Event dönemleri:

- Baseline MAE: `6.682`
- Event-Aware MAE: `6.687`

Normal dönemler:

- Baseline MAE: `2.177`
- Event-Aware MAE: `2.146`

Event-Aware model event dönemlerinde performans avantajı sağlamadı.

Genel MAE'deki küçük iyileşmenin event dönemlerinden değil, normal dönemlerdeki
küçük tahmin farklılıklarından kaynaklandığı görüldü.


#### 13. Event Feature Importance Analizi

Event-Aware XGBoost modelinin feature importance değerleri incelendi.

En önemli feature:

`lag_1 ≈ 0.646`

olarak bulundu.

Buna karşılık:

`event_recent_4w = 0.000`

importance değerine sahipti.

Bu sonuç XGBoost modelinin mevcut binary event feature'ını tahmin kararlarında
kullanmadığını gösterdi.

Bu nedenle mevcut event-aware yaklaşımın final forecasting pipeline'ına
eklenmemesine karar verildi.

Bu sonuç dış olayların trendler üzerinde etkili olmadığı anlamına gelmemektedir.
Mevcut `0/1` event temsilinin farklı event türleri ve büyüklüklerini yeterince
iyi ifade etmediği değerlendirildi.


#### 14. Anomaly Grafiklerinin Geliştirilmesi

ChatGPT, Gemini ve Claude için ayrı anomaly detection grafikleri oluşturuldu.

Grafiklerde:

- gerçek trend
- rolling mean
- anomaly noktaları
- anomaly score değerleri

birlikte gösterildi.

Anomaly score ile Google Trends puan farkının aynı şey olmadığı netleştirildi.

Örneğin ChatGPT'deki `7.70` anomaly score değeri 7.70 Google Trends puanı fark
anlamına gelmemektedir.

Bu değer, gözlemin geçmiş davranıştan yaklaşık 7.70 standart sapma uzak olduğunu
göstermektedir.


### Bugün Öğrenilen Kavramlar

- Anomaly detection
- Rolling window seçiminin etkisi
- Rolling mean ve rolling standard deviation
- Z-score tabanlı anomaly score
- Pozitif ve negatif anomaly
- Anomaly threshold
- Minimum absolute change
- Early-warning sistemi
- Trend monitoring
- Event validation
- Event-aware forecasting
- External / exogenous feature mantığı
- Data leakage ve event zamanlaması
- Lagged event feature
- Walk-forward evaluation
- Binary event feature'ların sınırlılıkları
- XGBoost feature importance
- Bir feature'ın eklenmesinin mutlaka modeli iyileştirmediği
- Genel performans ile event dönemlerindeki performansın ayrı değerlendirilmesi


### Sonraki Adımlar

- Anomaly detection kodunun gerekirse `src/` içerisine taşınması
- Monitoring ve anomaly sonuçlarının dashboard'a hazırlanması
- Forecast ve anomaly çıktılarının aynı dashboard üzerinde gösterilmesi
- Streamlit dashboard geliştirmeye başlanması
- Final forecasting pipeline'ının düzenlenmesi
- Model ve rapor çıktılarının organize edilmesi
- Event-aware forecasting yaklaşımının mevcut binary versiyonunun final modele dahil edilmemesi
- Daha zengin event veya dışsal veri kaynakları bulunursa event-aware yaklaşımın ileride yeniden değerlendirilmesi


## Day 11 — 17.08.2026

### Hedefler

- Güncel final model seçimlerini sabitlemek
- Final Prophet ve XGBoost modellerini tüm güncel veri üzerinde eğitmek
- Eğitilmiş model nesnelerini `models/` klasörüne kaydetmek
- Kaydedilen modelleri tekrar yükleyerek doğrulamak
- Model konfigürasyonlarını metadata olarak saklamak
- Kaydedilmiş modellerden yeniden eğitim yapmadan tahmin üreten final pipeline oluşturmak
- Final 4 haftalık forecast çıktısını kaydetmek
- Streamlit ve Plotly kullanarak interaktif dashboard geliştirmek
- Anomaly detection kodunu modüler hale getirerek dashboard'a bağlamak
- Forecast tabanlı early-warning mekanizması oluşturmak


### Yapılan Çalışmalar

#### 1. Final Model Seçimlerinin Sabitlenmesi

2026-08-09 tarihine kadar olan güncel Google Trends verisi kullanıldı.

Güncel veri seti toplam 159 haftalık gözlem içermektedir.

Önceki Time-Series Cross-Validation sonuçlarına göre final model seçimleri:

- ChatGPT → Prophet + XGBoost Ensemble
- Gemini → Naive
- Claude → Naive

olarak sabitlendi.

ChatGPT Ensemble için:

- Prophet ağırlığı → `0.5`
- XGBoost ağırlığı → `0.5`

olarak kullanılmaya devam edildi.

Final XGBoost parametreleri:

- `n_lags = 8`
- `n_estimators = 300`
- `max_depth = 2`
- `learning_rate = 0.03`
- `random_state = 42`

Final XGBoost feature seti:

- `lag_1 ... lag_8`
- `change_1`
- `change_2`

Prophet tarafında:

- `changepoint_prior_scale = 1.0`
- `yearly_seasonality = "auto"`

ayarları kullanıldı.


#### 2. Model Training Fonksiyonlarının `forecasting.py` İçerisine Taşınması

Final modelleri notebook içerisinde tekrar oluşturmak yerine model training
işlemlerinin modüler fonksiyonlara ayrılmasına karar verildi.

`src/forecasting.py` içerisine:

- `train_prophet_model()`
- `train_xgb_model()`

fonksiyonları eklendi.

`train_prophet_model()`:

- zaman serisini Prophet'in beklediği `ds` ve `y` formatına dönüştürüyor
- Prophet modelini oluşturuyor
- modeli verilen serinin tamamı üzerinde eğitiyor
- eğitilmiş Prophet model nesnesini döndürüyor

`train_xgb_model()`:

- lag feature'larını oluşturuyor
- `change_1` ve `change_2` feature'larını hesaplıyor
- XGBoost training verisini hazırlıyor
- modeli final parametrelerle eğitiyor
- eğitilmiş `XGBRegressor` nesnesini döndürüyor

Mevcut `forecast_prophet()` ve `forecast_xgb_recursive_with_change()`
fonksiyonları da bu training fonksiyonlarını kullanacak şekilde düzenlendi.

Böylece aynı model oluşturma ve `fit()` kodunun farklı yerlerde tekrar
edilmesi azaltıldı.


#### 3. Final Modellerin Tüm Güncel Veri Üzerinde Eğitilmesi

ChatGPT final Ensemble modelinin iki bileşeni olan Prophet ve XGBoost,
güncel ChatGPT serisinin tamamı kullanılarak yeniden eğitildi.

Bu aşamada amaç tekrar model karşılaştırması yapmak değildi.

Cross-validation ile model seçimi daha önce tamamlandığı için burada amaç:

seçilmiş modelleri mevcut tüm veri üzerinde eğiterek gerçek gelecek
tahminlerinde kullanılabilecek final model nesnelerini oluşturmaktı.


#### 4. Final Modellerin Kaydedilmesi

Eğitilmiş modellerin program kapatıldıktan sonra da tekrar kullanılabilmesi
için model persistence işlemleri yapıldı.

Prophet modeli:

`models/chatgpt_prophet_as_of_2026-08-09.json`

dosyasına kaydedildi.

XGBoost modeli:

`models/chatgpt_xgb_as_of_2026-08-09.json`

dosyasına kaydedildi.

Prophet için kendi JSON serialization yöntemi kullanıldı.

XGBoost için `save_model()` yöntemi kullanıldı.

Böylece modellerin daha sonra tekrar training yapılmadan yüklenebilmesi
amaçlandı.


#### 5. Model Persistence Doğrulaması

Model dosyalarının yalnızca oluşturulmuş olması yeterli kabul edilmedi.

Prophet modeli JSON dosyasından tekrar yüklendi ve orijinal modelle aynı
gelecek tarihler üzerinde tahmin üretildi.

Sonuç:

`Prophet predictions identical: True`

XGBoost modeli de JSON dosyasından tekrar yüklendi ve orijinal modelle aynı
feature girdisi üzerinde tahmin üretildi.

Sonuç:

`XGBoost predictions identical: True`

Böylece:

training → save → load → predict

işlem zincirinin her iki model için de doğru çalıştığı doğrulandı.


#### 6. JSON ve Metadata Yapısının İncelenmesi

Model saklama aşamasında JSON formatının amacı ayrıca incelendi.

JSON'un yapılandırılmış bilgiyi insan tarafından okunabilir ve farklı
programlama dilleri tarafından işlenebilir şekilde saklamak için kullanılan
bir veri formatı olduğu öğrenildi.

Model dosyalarının yanında ayrıca:

`models/model_metadata_as_of_2026-08-09.json`

dosyası oluşturuldu.

Metadata'nın modelin kendisi değil, model hakkında bilgi taşıyan üst veri
olduğu netleştirildi.

Metadata içerisinde:

- veri kesim tarihi
- forecast horizon
- Google Trends tahmin aralığı
- trend bazında seçilen modeller
- Ensemble ağırlıkları
- Prophet parametreleri
- XGBoost parametreleri
- XGBoost feature isimleri
- model dosyalarının isimleri
- persistence test sonuçları
- Gemini ve Claude için gerekli son gözlenen değerler

saklandı.

Bu yapı model konfigürasyonunun daha sonra anlaşılmasını ve yeniden
üretilebilirliğini kolaylaştırmaktadır.


#### 7. Final Forecasting Pipeline'ın Oluşturulması

Kaydedilmiş modellerin notebook dışından kullanılabilmesi amacıyla:

`src/pipeline.py`

dosyası oluşturuldu.

Pipeline içerisinde:

- `load_model_metadata()`
- `load_prophet_model()`
- `load_xgb_model()`
- `forecast_prophet_loaded()`
- `forecast_xgb_loaded()`
- `forecast_naive_loaded()`
- `generate_final_forecast()`

fonksiyonları geliştirildi.

`generate_final_forecast()`:

1. Metadata dosyasını yüklüyor.
2. Veri tarihi ile model eğitim tarihini karşılaştırıyor.
3. Kaydedilmiş Prophet modelini yüklüyor.
4. Kaydedilmiş XGBoost modelini yüklüyor.
5. ChatGPT için Prophet ve XGBoost tahminlerini birleştiriyor.
6. Gemini için Naive forecast üretiyor.
7. Claude için Naive forecast üretiyor.
8. Üç trendin tahminlerini tek DataFrame olarak döndürüyor.

Bu yapı sayesinde final tahmin üretmek için Prophet ve XGBoost modellerinin
her seferinde yeniden eğitilmesine gerek kalmadı.


#### 8. Kaydedilmiş Modellerle Final Forecast Üretilmesi

Yeni pipeline kaydedilmiş model dosyaları kullanılarak çalıştırıldı.

Elde edilen final tahminler:

| Tarih | ChatGPT | Gemini | Claude |
|---|---:|---:|---:|
| 2026-08-16 | 70.248219 | 40.0 | 15.0 |
| 2026-08-23 | 70.850414 | 40.0 | 15.0 |
| 2026-08-30 | 71.373637 | 40.0 | 15.0 |
| 2026-09-06 | 72.022927 | 40.0 | 15.0 |

Kaydedilmiş modellerden üretilen tahminlerin, daha önce doğrudan model
eğitimiyle elde edilen final tahminlerle aynı olduğu görüldü.

Bu sonuç final inference pipeline'ın doğru çalıştığını doğruladı.


#### 9. Final Forecast Çıktısının Kaydedilmesi

Üretilen 4 haftalık final forecast:

`reports/final_forecast_as_of_2026-08-09.csv`

dosyasına kaydedildi.

CSV dosyası tekrar pandas ile okunarak pipeline çıktısıyla karşılaştırıldı.

`np.allclose()` ile yapılan kontrolde kaydedilmiş değerlerin orijinal
forecast çıktısıyla aynı olduğu doğrulandı.


#### 10. Streamlit Dashboard'un Başlatılması

Final forecasting pipeline hazır hale geldikten sonra kullanıcı arayüzü
aşamasına geçildi.

Proje ana klasöründe:

`app.py`

dosyası oluşturuldu.

Streamlit uygulaması:

`streamlit run app.py`

komutuyla yerel olarak çalıştırıldı.

İlk çalıştırmada Streamlit local server'ın sorunsuz şekilde açıldığı
doğrulandı.


#### 11. Dashboard'un Final Forecasting Pipeline'a Bağlanması

Dashboard gerçek proje dosyalarına bağlandı.

`app.py` içerisinde:

- güncel processed CSV verisi okunuyor
- model metadata dosyası yükleniyor
- `models/` klasöründeki model artifact'ları kullanılıyor
- `generate_final_forecast()` çağrılıyor

Bu nedenle dashboard üzerinde trend seçildiğinde modeller yeniden
eğitilmiyor.

Kaydedilmiş final modeller doğrudan inference amacıyla kullanılıyor.


#### 12. Dashboard Trend Seçimi ve Bilgi Kartları

Streamlit `selectbox` kullanılarak kullanıcıya:

- ChatGPT
- Gemini
- Claude

seçenekleri sunuldu.

Seçilen trende göre dashboard içeriği otomatik olarak güncellenmektedir.

Üç temel bilgi kartı oluşturuldu:

- Son Gözlenen Skor
- 4 Hafta Sonrası Tahmin
- Final Model

4 hafta sonrası tahmin kartında ayrıca mevcut değer ile forecast horizon
sonundaki değer arasındaki değişim gösterilmektedir.


#### 13. Plotly ile İnteraktif Geçmiş ve Forecast Grafiği

Plotly kullanılarak seçilen trendin:

- gerçek geçmiş Google Trends verisi
- gelecek 4 haftalık final forecast'u

aynı grafik üzerinde gösterildi.

Gerçek veri düz çizgiyle, gelecek forecast ise farklı çizgi biçimi ve
marker'larla ayrıldı.

Forecast çizgisinin başlangıcına son gerçek gözlem eklenerek geçmiş ve
gelecek arasında görsel bağlantı sağlandı.

Google Trends değerleri doğal olarak 0-100 arasında olduğu için grafik
Y ekseni de bu aralıkta tutuldu.

Plotly hover özelliği sayesinde tarih ve trend skorları interaktif olarak
incelenebilmektedir.


#### 14. Forecast Tablosunun Dashboard'a Eklenmesi

4 haftalık final forecast değerleri grafik dışında ayrıca tablo olarak
gösterildi.

Böylece kullanıcı tahminleri:

- grafik üzerinde görsel olarak
- tablo üzerinde sayısal olarak

inceleyebilmektedir.


#### 15. Anomaly Detection Kodunun `monitoring.py` İçerisine Taşınması

Day 10'da notebook içerisinde geliştirilen anomaly detection yaklaşımı
modüler hale getirildi.

Yeni dosya:

`src/monitoring.py`

oluşturuldu.

`detect_anomalies()` fonksiyonu bu dosyaya taşındı.

Final monitoring parametreleri:

- `window = 12`
- `threshold = 3.5`
- `min_absolute_change = 5`

olarak korundu.

Rolling referans hesaplamasında `shift(1)` kullanılarak mevcut gözlemin
kendi geçmiş referans ortalamasına dahil edilmemesi sağlandı.


#### 16. Güncel Anomaly Monitoring'in Dashboard'a Eklenmesi

Dashboard üzerinde seçilen trend için güncel anomaly durumu hesaplanmaya
başlandı.

Kullanıcıya:

- son gözlemin anomaly olup olmadığı
- anomaly score

gösterildi.

2026-08-09 itibarıyla:

- ChatGPT → Anomaly Score ≈ `0.47`
- Gemini → Anomaly Score ≈ `-0.54`
- Claude → Anomaly Score ≈ `-1.26`

sonuçları elde edildi.

Üç trend için de son gözlemde güçlü anomaly bulunmadı.


#### 17. Forecast Tabanlı Early-Warning Mekanizmasının Oluşturulması

Anomaly detection'dan ayrı olarak geleceğe yönelik bir early-warning
mekanizması geliştirildi.

`src/monitoring.py` içerisine:

`detect_rising_trend_signal()`

fonksiyonu eklendi.

Bu fonksiyon:

- mevcut değer ile forecast horizon sonundaki değer arasındaki toplam değişimi
- forecast içerisindeki pozitif haftalık değişimlerin oranını

hesaplamaktadır.

Başlangıç eşikleri:

- `min_total_increase = 5`
- `min_positive_ratio = 0.75`

olarak belirlendi.

Yükselen Trend Sinyali oluşması için:

- toplam artışın en az 5 Google Trends puanı olması
- haftalık değişimlerin en az %75'inin pozitif olması

şartı kullanıldı.

Bu eşiklerin optimize edilmiş nihai istatistiksel parametreler olmadığı,
yorumlanabilir başlangıç kuralları olduğu not edildi.


#### 18. Anomaly Detection ve Early-Warning Ayrımının Netleştirilmesi

İki monitoring kavramının farklı amaçlara hizmet ettiği netleştirildi.

Anomaly Detection:

"Mevcut veya geçmiş gözlem yakın geçmiş davranışına göre sıra dışı mı?"

sorusuna cevap vermektedir.

Early-Warning:

"Final forecasting modeli gelecekte belirgin ve devamlı bir yükseliş
öngörüyor mu?"

sorusuna cevap vermektedir.

Böylece geçmiş/mevcut monitoring ile gelecek tahmin sinyali birbirinden
ayrıldı.


#### 19. Güncel Early-Warning Sonuçları

Mevcut final forecast'larda üç trend için de güçlü yükselen trend sinyali
oluşmadı.

ChatGPT:

yaklaşık `70 → 72`

şeklinde yukarı yönlü tahmin edilmesine rağmen toplam artış yaklaşık 2 puan
olduğu için 5 puanlık alarm eşiğinin altında kaldı.

Gemini:

`40 → 40`

Claude:

`15 → 15`

şeklinde sabit Naive forecast üretti.

Bu nedenle üç trend için de güncel güçlü yükselen trend alarmı oluşmadı.


#### 20. Geçmiş Anomaly Noktalarının İnteraktif Grafiğe Eklenmesi

Anomaly detection sonucunda geçmişte `Is_Anomaly=True` olan noktalar Plotly
grafiğine ayrıca eklendi.

Anomaly noktaları ayrı marker'larla gösterildi.

Kullanıcı bu noktaların üzerine geldiğinde:

- tarih
- gerçek trend skoru
- anomaly score

bilgilerini görebilmektedir.

Böylece dashboard yalnızca mevcut anomaly durumunu göstermekle kalmayıp
geçmişte tespit edilen sıra dışı hareketleri de görselleştirmeye başladı.


#### 21. Streamlit Import Probleminin Çözülmesi

Dashboard geliştirilirken:

`ImportError: cannot import name 'detect_rising_trend_signal' from 'src.monitoring'`

hatası alındı.

`app.py` içerisinden import edilmeye çalışılan fonksiyonun
`monitoring.py` içerisinde doğru şekilde tanımlanıp kaydedildiği kontrol edildi.

Fonksiyon doğru isimle kaydedildikten ve Streamlit yeniden çalıştırıldıktan
sonra import problemi çözüldü.


#### 22. Gün Sonu Proje Yapısı

Day 11 sonunda özellikle aşağıdaki proje bileşenleri oluşturulmuş veya
güncellenmiş oldu:

trend-forecast-project/
│
├── app.py
│
├── data/
│   └── processed/
│       └── google_trends_ai_3y_updated_2026-08-09.csv
│
├── models/
│   ├── chatgpt_prophet_as_of_2026-08-09.json
│   ├── chatgpt_xgb_as_of_2026-08-09.json
│   └── model_metadata_as_of_2026-08-09.json
│
├── reports/
│   └── final_forecast_as_of_2026-08-09.csv
│
├── src/
│   ├── forecasting.py
│   ├── monitoring.py
│   └── pipeline.py
│
└── notebooks/
    └── 11_final_pipeline_dashboard.ipynb

### Bugün Öğrenilen Kavramlar

Bugün Öğrenilen Kavramlar
Model training ve inference farkı
Final model training
Model persistence
Model artifact
Serialization ve deserialization
JSON veri formatı
Metadata ve üst veri kavramı
Model save/load doğrulaması
Reproducibility
Inference pipeline
Kaydedilmiş modelden tahmin üretme
Streamlit uygulama yapısı
st.set_page_config()
st.selectbox()
st.metric()
st.columns()
st.error() ve st.stop()
Plotly Figure
Plotly Scatter
Plotly trace mantığı
hovertemplate
customdata
Dashboard ile forecasting backend'inin ayrılması
Anomaly monitoring
Forecast tabanlı early-warning
Anomaly detection ile early-warning arasındaki fark
Dashboard üzerinde model sonuçlarının interaktif sunulması

### Sonraki Adımlar

- Forecast uncertainty / confidence interval yaklaşımını final model yapısına uygun şekilde geliştirmek
- Dashboard arayüzünü ve kullanıcı deneyimini iyileştirmek
- Dashboard üzerinde hata yönetimi ve edge-case kontrollerini geliştirmek
- `pipeline.py` ve `monitoring.py` fonksiyonlarını uçtan uca test etmek
- Yeni veri geldiğinde modelin yeniden eğitilmesi ve model artifact'larının güncellenmesi sürecini netleştirmek
- `requirements.txt` dosyasını güncel kullanılan kütüphanelerle güncellemek
- README dosyasına final model yapısı, pipeline, model artifact'ları ve Streamlit kullanımını eklemek
- Projeyi temiz bir ortamda baştan çalıştırarak kurulum ve çalıştırma adımlarını doğrulamak
- Dashboard ve forecasting sonuçlarından final rapor için gerekli görselleri biriktirmek
- Final staj raporunu hazırlamak
- Final proje sunumunu ve dashboard demo akışını hazırlamak

## Day 12 — 18.08.2026

### Hedefler

- Final forecast'lar için belirsizlik bilgisinin oluşturulması
- Cross-validation residual'larından ampirik prediction interval elde edilmesi
- Prediction interval yaklaşımının doğrulanması
- Belirsizlik bilgisinin Streamlit dashboard'a entegre edilmesi

### Yapılan Çalışmalar

1. Final modeller için out-of-sample residual'lar oluşturuldu.
   - Gemini ve Claude için Naive CV residual'ları kullanıldı.
   - ChatGPT için final Prophet + XGBoost Ensemble modelinin CV residual'ları
     ayrıca üretildi.
   - Her trend için 12 fold × 4 hafta = 48 residual elde edildi.

2. Residual dağılımları analiz edildi.
   - Mean, median, standart sapma ve uç değerler incelendi.
   - Q10-Q90 merkezi %80 ampirik prediction interval yaklaşımı seçildi.
   - Residual dağılımlarının simetrik olmadığı görüldüğü için simetrik
     `forecast ± hata` yaklaşımı kullanılmadı.

3. Forecast horizon etkisi incelendi.
   - Horizon 1-4 residual'ları ayrı ayrı değerlendirildi.
   - Horizon ilerledikçe belirsizliğin artabileceğine dair sinyal gözlendi.
   - Ancak horizon başına yalnızca 12 residual bulunduğundan final sistemde
     daha kararlı olan pooled 48-residual yaklaşımı tercih edildi.

4. Final interval kalibrasyonları elde edildi.
   - ChatGPT: Q10 ≈ -7.609, Q90 ≈ 5.171
   - Gemini: Q10 ≈ -5.300, Q90 ≈ 5.000
   - Claude: Q10 ≈ -1.000, Q90 ≈ 3.300

5. Ampirik coverage kontrolü yapıldı.
   - ChatGPT: %79.17
   - Gemini: %85.42
   - Claude: %81.25
   - Sonuçların hedeflenen %80 seviyesine yakın olduğu görüldü.

6. Final forecast + prediction interval sonuçları kaydedildi.
   - `reports/final_forecast_with_intervals_as_of_2026-08-09.csv`

7. Prediction interval metadata oluşturuldu.
   - `models/prediction_interval_metadata_as_of_2026-08-09.json`
   - Interval seviyesi, Q10-Q90, CV yapısı, residual sayıları ve final model
     bilgileri saklandı.

8. Streamlit dashboard güncellendi.
   - Prediction interval metadata uygulamaya bağlandı.
   - Seçilen trend için Lower/Upper sınırları otomatik hesaplandı.
   - Plotly forecast grafiğine gölgeli %80 ampirik prediction interval eklendi.
   - Forecast tablosu Tahmin / Alt Sınır / Üst Sınır şeklinde güncellendi.
   - ChatGPT, Gemini ve Claude için dashboard çıktıları doğrulandı.

9. Final yapısal validation kontrolleri gerçekleştirildi.
   - `Lower <= Forecast <= Upper`
   - NaN bulunmaması
   - Bütün değerlerin 0-100 arasında olması
   - Tüm kontroller başarılı (`True`) sonuçlandı.

### Bugün Öğrenilen Kavramlar

- Residual dağılımından ampirik prediction interval oluşturma
- Quantile ve merkezi prediction interval
- Q10-Q90 yaklaşımı
- Prediction interval ile MAE tabanlı hata bandı arasındaki fark
- Pooled residual ve horizon-specific residual yaklaşımı
- Ampirik coverage
- Prediction interval kalibrasyonu ile bağımsız validation arasındaki fark
- Plotly `fill="tonexty"` ile belirsizlik bandı oluşturma
- Calibration metadata'nın inference sisteminden ayrılması

### Sonraki Adımlar

- Proje dokümantasyonunun son halinin hazırlanması
- README ve proje kullanım açıklamalarının güncellenmesi
- Final staj raporu için proje sürecinin ve sonuçlarının düzenlenmesi
- Gerekirse sunum/demo materyallerinin hazırlanması
