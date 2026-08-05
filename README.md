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

Veri toplama, preprocessing, ilk keşifsel veri analizi ve zaman serisi decomposition aşamaları tamamlanmıştır. Sonraki aşamada tahmin modelleri için veri hazırlığı ve modelleme çalışmaları yapılacaktır.
