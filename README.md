# Trend Forecast Project

## Proje Hakkında

Bu proje, coTalent AI Takımı staj programı kapsamında geliştirilen **Veri Tabanlı Trend Tahminleme ve Öngörü Motoru** çalışmasıdır.

Projenin amacı; zaman serisi verilerini kullanarak teknoloji ve kavramların geçmiş trendlerini analiz etmek ve ilerleyen aşamalarda gelecekteki ilgi seviyelerini tahmin edebilen uçtan uca bir veri bilimi pipeline'ı geliştirmektir.

## Kullanılan Teknolojiler

- Python
- Pandas
- NumPy
- Pytrends
- Matplotlib
- Seaborn
- Statsmodels
- Prophet
- XGBoost
- Scikit-learn

Projenin ilerleyen aşamalarında LightGBM, Plotly ve Streamlit kullanılması planlanmaktadır.

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
## Gün Özetleri
### İlk Gün Çalışmaları

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

### 6. Gün

- XGBoost ile lag tabanlı forecasting modeli geliştirildi.
- 4 lag ve 8 lag yapıları karşılaştırıldı; 8 lag daha iyi performans verdi.
- `change_1` ve `change_2` feature'ları eklendi.
- Recursive forecasting ve 12 fold × 4 haftalık time-series cross-validation uygulandı.
- `max_depth`, `n_estimators` ve `learning_rate` için tuning yapıldı.
- En iyi XGBoost ayarları:
  - `n_estimators=300`
  - `max_depth=2`
  - `learning_rate=0.03`
- Final sonuç:
  - MAE: `4.356`
  - RMSE: `4.902`
- XGBoost değerlendirme fonksiyonu `src/forecasting.py` içerisine taşındı.

### 7. Gün

- Tüm modeller aynı 149 haftalık tarih aralığında yeniden değerlendirildi.
- Naive, ARIMA, Prophet ve tuned XGBoost aynı 12 fold × 4 haftalık
  time-series cross-validation yapısında karşılaştırıldı.
- Tekil modeller arasında en iyi sonuç Prophet ile elde edildi:
  - MAE: `4.211`
  - RMSE: `4.745`
- Fold bazlı analizde XGBoost'un daha fazla fold kazandığı ancak bazı dönemlerde
  daha büyük hatalar yaptığı görüldü.
- Prophet ve XGBoost tahminleri birleştirilerek ensemble model oluşturuldu.
- Eşit ağırlıklı `%50 Prophet + %50 XGBoost` ensemble en iyi genel sonucu verdi:
  - MAE: `3.911`
  - RMSE: `4.520`
- Farklı ensemble ağırlıkları test edildi ve performans farkları küçük olduğu için
  daha basit olan `0.5 / 0.5` kombinasyonu seçildi.
- Ensemble değerlendirme fonksiyonu `src/forecasting.py` içerisine eklendi.

### 8. Gün

- ChatGPT üzerinde geliştirilen modelleme pipeline'ı Gemini ve Claude trend serilerine uygulandı.
- Naive, ARIMA, Prophet, XGBoost ve Ensemble modelleri aynı 12 fold × 4 haftalık time-series cross-validation yapısında karşılaştırıldı.
- Gemini için en iyi sonuç ARIMA ile elde edildi:
  - MAE: `6.582`
  - RMSE: `7.403`
- Claude için en iyi sonuç ARIMA ile elde edildi:
  - MAE: `1.317`
  - RMSE: `1.535`
- ChatGPT, Gemini ve Claude sonuçları tek tabloda karşılaştırıldı.
- ChatGPT için en iyi genel yaklaşım Prophet + XGBoost Ensemble olarak kaldı:
  - MAE: `3.911`
  - RMSE: `4.520`
- Her trend serisi için cross-validation sonuçlarına göre en iyi modeli otomatik seçen `select_best_model()` fonksiyonu geliştirildi.
- Seçilen modeller kullanılarak gelecek 4 haftalık final tahminler üretildi:
  - ChatGPT → Ensemble
  - Gemini → ARIMA
  - Claude → ARIMA
- XGBoost için recursive future forecasting yapabilen `forecast_xgb_recursive_with_change()` fonksiyonu geliştirildi.
- Final tahminler tek tabloda birleştirilerek `reports/` klasörüne kaydedildi.
- Tahmin dosyalarının isimlerine son gözlem tarihi eklendi:
  - `final_forecast_as_of_YYYY-MM-DD.csv`
- Gemini'deki ani trend artışı üzerinden dışsal olayların forecasting modellerine etkisi incelendi ve event-aware forecasting ileriki geliştirme olarak planlandı.

### 9. Gün

- Google Trends verisi yeni haftalık verilerle güncellendi.
- Eski ve yeni veri arasındaki ortak tarihler karşılaştırılarak ölçek farklılıkları incelendi.
- Geçmiş veri yeniden ölçeklenmeden yalnızca yeni haftaların mevcut veri setine eklenmesine karar verildi.
- Önceki gün üretilen tahminler yeni gerçekleşen verilerle karşılaştırılarak ilk gerçek future validation gerçekleştirildi.
- Güncellenmiş veriyle Naive, ARIMA, Prophet, XGBoost ve Ensemble modelleri yeniden değerlendirildi.
- Gemini ARIMA modelinin ani trend artışı sonrasında 100'ün üzerinde gerçek dışı tahminler üretebildiği tespit edildi.
- Google Trends skorlarının doğal `0–100` aralığı dikkate alınarak bounded forecasting yaklaşımı eklendi.
- Clipping sonrasında Gemini ARIMA MAE değeri yaklaşık `10.974` değerinden `5.635` değerine düştü.
- Güncel model karşılaştırması sonucunda seçilen modeller:
  - ChatGPT → Prophet + XGBoost Ensemble
  - Gemini → Naive
  - Claude → Naive
- Güncellenmiş modeller kullanılarak yeni 4 haftalık final tahminler üretildi.
- Ani trend değişimlerini tespit etmek amacıyla rolling mean, rolling standard deviation ve anomaly score kullanan ilk anomaly detection prototipi oluşturuldu.
- Gemini'nin 2025 Ağustos–Eylül dönemindeki ani trend artışı anomaly detection ile tespit edildi.
- Sıfır standart sapma nedeniyle oluşabilecek `inf` değerleri ve küçük değişimlerden kaynaklanan gereksiz alarmlar incelendi.
- Anomaly detection için window, threshold ve minimum değişim parametrelerinin ileride optimize edilmesine karar verildi.

### 10. Gün

- Anomaly detection sistemi geliştirildi ve rolling window, threshold ve minimum değişim parametreleri karşılaştırıldı.
- Mevcut prototip için `window=12`, `threshold=3.5` ve `min_absolute_change=5` değerleri seçildi.
- ChatGPT, Gemini ve Claude için anomaly noktaları tespit edilerek zaman serisi üzerinde görselleştirildi.
- Güncel trend durumlarını gösteren early-warning ve monitoring çıktısı oluşturuldu.
- Anomaly tarihleri dış gelişmelerle karşılaştırılarak event validation çalışması yapıldı.
- Gemini için tarihsel event kataloğu ve event-based feature'lar oluşturuldu.
- Baseline ve Event-Aware XGBoost modelleri 1 haftalık walk-forward evaluation ile karşılaştırıldı.
- Event-Aware model event dönemlerinde performans avantajı sağlamadı.
- `event_recent_4w` feature importance değeri `0.0` olarak bulundu.
- Mevcut binary event feature yaklaşımının final forecasting pipeline'ına dahil edilmemesine karar verildi.

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

## Durum

Veri toplama, preprocessing, EDA, decomposition ve forecasting modelleme aşamaları tamamlanmıştır.

Naive, ARIMA, Prophet, XGBoost ve Ensemble modelleri ChatGPT, Gemini ve Claude trend serileri üzerinde time-series cross-validation ile değerlendirilmiş ve her trend için en uygun model seçilmiştir.

Güncel olarak seçilen modeller:

- ChatGPT → Prophet + XGBoost Ensemble
- Gemini → Naive
- Claude → Naive

Google Trends skorları için `0–100` bounded forecasting yaklaşımı uygulanmakta ve seçilen modellerle 4 haftalık tahminler üretilmektedir.

Forecasting pipeline'ına ek olarak anomaly detection ve early-warning prototipi geliştirilmiştir. ChatGPT, Gemini ve Claude için olağan dışı trend hareketleri tespit edilebilmekte ve güncel monitoring durumu oluşturulabilmektedir.

Event-aware forecasting yaklaşımı deneysel olarak test edilmiş ancak mevcut binary event feature'ının XGBoost performansına anlamlı katkı sağlamadığı görülmüştür. Bu nedenle mevcut event-aware yaklaşım final forecasting modeline dahil edilmemiştir.

Bir sonraki aşamada anomaly ve forecasting çıktılarının dashboard'a hazırlanması, Streamlit geliştirmesi ve final pipeline düzenlemeleri planlanmaktadır.
