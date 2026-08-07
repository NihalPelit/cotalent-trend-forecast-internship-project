# Trend Forecast Project

## Proje Hakkında

Bu proje, coTalent AI Takımı staj programı kapsamında geliştirilen **Veri Tabanlı Trend Tahminleme ve Öngörü Motoru** çalışmasıdır.

Projenin amacı; zaman serisi verilerini kullanarak teknoloji ve kavramların geçmiş trendlerini analiz etmek ve ilerleyen aşamalarda gelecekteki ilgi seviyelerini tahmin edebilen uçtan uca bir veri bilimi pipeline'ı geliştirmektir.

## Kullanılan Teknolojiler

* Python
* Pandas
* NumPy
* Pytrends
* Matplotlib
* Seaborn
* Statsmodels

Projenin ilerleyen aşamalarında Prophet, ARIMA/SARIMAX, XGBoost/LightGBM, Plotly ve Streamlit kullanılması planlanmaktadır.

## Proje Yapısı

```text
trend-forecast-project/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
├── models/
├── reports/
├── README.md
├── requirements.txt
├── daily_notes.md
└── questions.md
```

## İlk Gün Çalışmaları

İlk gün kapsamında:

* Python sanal ortamı oluşturuldu.
* Temel proje bağımlılıkları yüklendi.
* Pytrends kütüphanesi incelendi.
* `TrendReq`, `build_payload()` ve `interest_over_time()` yapıları öğrenildi.
* Google Trends üzerinden örnek zaman serisi verisi çekildi.
* Pandas DataFrame yapısı incelendi.
* Eksik değer ve zaman aralığı kontrolleri yapıldı.
* Linear interpolation yöntemi gerçek veri üzerinde deneysel olarak test edildi.

### 2. Gün

- Tekrar kullanılabilir Google Trends veri çekme fonksiyonu geliştirildi.
- Girdi doğrulama (input validation) ve API hata yönetimi eklendi.
- Retry ve exponential backoff mekanizması geliştirildi.
- Aşağıdaki terimler için 3 yıllık dünya geneli Google Trends verisi çekildi:
  - ChatGPT
  - Gemini
  - Claude
- Raw ve processed veri akışı oluşturuldu.
- Tamamlanmamış (`isPartial=True`) Google Trends satırları kaldırıldı.
- Eksik değer ve eksik hafta kontrolleri tamamlandı.
- Temiz veri seti oluşturuldu.
- İlk keşifsel veri analizi (EDA) ve görselleştirme işlemleri yapıldı.
- Pytrends çıktısı Google Trends web verisi ile karşılaştırıldı.
- Doğrulama amacıyla haftalık veri aylık frekansa dönüştürüldü.

### 3. Gün

- Zaman serisi decomposition yöntemi incelendi.
- `statsmodels` kullanılarak haftalık Google Trends verilerine additive decomposition uygulandı.
- Observed, trend, seasonal ve residual bileşenleri analiz edildi.
- Haftalık veri için `period=52` kullanılarak yaklaşık yıllık seasonality yapısı incelendi.
- ChatGPT'nin uzun vadeli trend değişimi analiz edildi.
- Büyük pozitif ve negatif residual değerlerinin bulunduğu haftalar tespit edildi.
- Önemli residual dönemleri dış gelişmeler ve OpenAI duyuruları ile karşılaştırıldı.
- Residual değerlerin dış olayların nedenini kanıtlamadığı, sıra dışı dönemleri tespit etmek için kullanılabileceği değerlendirildi.
- ChatGPT, Gemini ve Claude için uzun vadeli trendler karşılaştırıldı.
- Trend değişimleri hesaplandı:
  - ChatGPT: yaklaşık `+53.41`
  - Gemini: yaklaşık `+34.69`
  - Claude: yaklaşık `+8.68`
- Decomposition işlemleri tekrar kullanılabilir hale getirilerek `src/time_series.py` içerisine taşındı.
- `decompose_series()` fonksiyonu geliştirildi.
- Decomposition sonuçlarını DataFrame'e dönüştürmek için `decomposition_to_dataframe()` fonksiyonu oluşturuldu.
- `expected = trend + seasonal` değeri hesaplanarak gerçek değerlerle decomposition temel seviyesi karşılaştırılabilir hale getirildi.
- Notebook içerisinden `src` modüllerinin kullanımı düzenlendi.
- `requirements.txt` güncellenerek Statsmodels ve güncel proje bağımlılıkları kaydedildi.

### 4. Gün

- Forecasting aşamasına geçildi.
- ChatGPT zaman serisi zaman sırası korunarak train ve test setlerine ayrıldı.
- Son 12 haftalık veri test seti olarak kullanıldı.
- Gerçek tahmin modellerini karşılaştırmak amacıyla naive baseline model oluşturuldu.
- Naive baseline için:
  - MAE: `4.17`
  - RMSE: `5.05`
  sonuçları elde edildi.
- Gerçek test değerleri ile baseline tahminleri görselleştirildi.
- ARIMA modelinin `p`, `d` ve `q` parametrelerinin temel mantığı incelendi.
- Zaman serisinin durağanlığı Augmented Dickey-Fuller (ADF) testi ile kontrol edildi.
- Ham ChatGPT serisinin durağan olmadığı gözlemlendi.
- Birinci dereceden differencing sonrasında seri durağan hale geldi ve `d=1` aday olarak belirlendi.
- ACF ve PACF grafikleri kullanılarak ARIMA için olası `p` ve `q` değerleri incelendi.
- Farklı ARIMA konfigürasyonları test edildi:
  - `ARIMA(2,1,0)`
  - `ARIMA(0,1,2)`
  - `ARIMA(2,1,2)`
  - `ARIMA(1,1,1)`
- Modeller aynı test dönemi üzerinde MAE ve RMSE metrikleri ile karşılaştırıldı.
- En iyi tek-test sonucu `ARIMA(1,1,1)` modeli ile elde edildi:
  - MAE: `3.71`
  - RMSE: `4.51`
- `ARIMA(1,1,1)` naive baseline modelinden daha düşük hata verdi.
- Tek bir test döneminin model seçimi için yeterli olmayabileceği değerlendirildi.
- Bir sonraki aşamada time-series cross-validation ile modellerin farklı zaman dönemlerindeki performanslarının test edilmesine karar verildi.

### 5. Gün

- Time Series Cross-Validation ile modeller birden fazla zaman aralığında değerlendirildi.
- Yaklaşık 30 günlük tahmin hedefi için 12 fold ve 4 haftalık test periyodu kullanıldı.
- Naive, ARIMA ve Prophet modelleri MAE ve RMSE metrikleriyle karşılaştırıldı.
- Prophet için `changepoint_prior_scale` tuning yapıldı ve `1.0` değeri seçildi.
- En iyi sonuç Prophet (`cps=1.0`) modeliyle elde edildi:
  - MAE: 4.303
  - RMSE: 4.826
- Prophet değerlendirme ve tahmin fonksiyonları `src/forecasting.py` içerisine taşındı.

## Veri

Oluşturulan ham ve işlenmiş veri setleri aşağıdaki klasörlerde saklanmaktadır:

```text
data/raw/
data/processed/
```

## Kurulum

Sanal ortam oluşturmak:

```bash
python3 -m venv cotale-env
```

Sanal ortamı aktif etmek:

```bash
source cotale-env/bin/activate
```

Bağımlılıkları yüklemek:

```bash
pip install -r requirements.txt
```


## Durum

Proje geliştirme aşamasındadır.
Veri toplama, preprocessing, keşifsel veri analizi, time series decomposition,
baseline forecasting, ARIMA modelleme ve time-series cross-validation
çalışmaları tamamlanmıştır.

Yaklaşık 30 günlük tahmin hedefi için 4 haftalık cross-validation uygulanmış;
Naive, ARIMA ve Prophet modelleri farklı zaman dönemlerinde karşılaştırılmıştır.
Prophet modeli için `changepoint_prior_scale` optimizasyonu yapılmış ve
`cps=1.0` seçilmiştir.

Mevcut cross-validation değerlendirmesinde Prophet (`cps=1.0`) en düşük
MAE ve RMSE değerlerini vermiştir. Sonraki aşamada lag feature'lar
oluşturularak XGBoost/LightGBM modelleri geliştirilecek ve mevcut
zaman serisi modelleriyle karşılaştırılacaktır.
