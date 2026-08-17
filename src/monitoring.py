# --------------------------------------------------
# Trend monitoring and anomaly detection
# --------------------------------------------------

# NumPy:
# rolling standard deviation sıfır olduğunda
# güvenli hesaplama yapmak ve NaN kullanmak için.
import numpy as np

# Pandas:
# zaman serileri ve rolling hesaplamalar için.
import pandas as pd


def detect_anomalies(
    series: pd.Series,
    window: int = 12,
    threshold: float = 3.5,
    min_absolute_change: float = 5.0,
) -> pd.DataFrame:
    """
    Bir zaman serisindeki sıra dışı hareketleri
    rolling mean ve standard deviation kullanarak tespit eder.

    Parameters
    ----------
    series : pd.Series
        İncelenecek zaman serisi.

    window : int, default=12
        Karşılaştırmada kullanılacak geçmiş hafta sayısı.

    threshold : float, default=3.5
        Bir gözlemin anomaly kabul edilmesi için gereken
        minimum standard deviation uzaklığı.

    min_absolute_change : float, default=5.0
        Çok küçük değişimlerin anomaly olarak işaretlenmesini
        önlemek için gereken minimum puan farkı.

    Returns
    -------
    pd.DataFrame
        Gerçek değer, rolling mean, anomaly score
        ve anomaly durumunu içeren tablo.
    """

    # --------------------------------------------------
    # Sonuç DataFrame'ini oluşturma
    # --------------------------------------------------

    result = pd.DataFrame({"Value": series.astype(float)})

    # --------------------------------------------------
    # Geçmiş referans ortalaması
    # --------------------------------------------------

    # shift(1):
    # mevcut haftayı rolling hesaplamadan çıkarır.
    #
    # Bunun nedeni çok önemli:
    #
    # Bir haftanın sıra dışı olup olmadığını ölçerken
    # o haftanın kendi değerini referans geçmişe
    # dahil etmek istemiyoruz.
    #
    # Böylece mevcut gözlem yalnızca
    # ÖNCEKİ haftalarla karşılaştırılır.
    shifted_series = series.shift(1)

    # rolling(window=12):
    # her tarih için önceki 12 haftalık
    # hareketli pencere oluşturur.
    result["Rolling_Mean"] = shifted_series.rolling(window=window).mean()

    # Aynı geçmiş pencerenin standard deviation'ı.
    #
    # Bu değer bize geçmiş dönemin ne kadar
    # oynak olduğunu söyler.
    result["Rolling_Std"] = shifted_series.rolling(window=window).std()

    # --------------------------------------------------
    # Ortalama ile mevcut değer arasındaki fark
    # --------------------------------------------------

    result["Absolute_Change"] = (result["Value"] - result["Rolling_Mean"]).abs()

    # --------------------------------------------------
    # Anomaly score
    # --------------------------------------------------

    # Standard deviation 0 ise doğrudan bölme yapmak
    # mümkün değildir.
    #
    # replace(0, np.nan):
    # sıfır değerleri geçici olarak NaN yaparak
    # sıfıra bölme hatasını önlüyoruz.
    safe_std = result["Rolling_Std"].replace(
        0,
        np.nan,
    )

    # Anomaly score:
    #
    # mevcut değer - geçmiş ortalama
    # --------------------------------
    # geçmiş standard deviation
    #
    # Örneğin:
    #
    # score = +4
    #
    # mevcut değerin geçmiş ortalamadan
    # yaklaşık 4 standard deviation yukarıda
    # olduğu anlamına gelir.
    result["Anomaly_Score"] = (result["Value"] - result["Rolling_Mean"]) / safe_std

    # --------------------------------------------------
    # Anomaly kararı
    # --------------------------------------------------

    # Bir gözlemi anomaly saymak için:
    #
    # 1. Mutlak değişim en az min_absolute_change olmalı
    #
    # VE
    #
    # 2. anomaly score threshold'u aşmalı
    #    VEYA geçmiş std tamamen 0 olmalı.
    result["Is_Anomaly"] = (result["Absolute_Change"] >= min_absolute_change) & (
        (result["Anomaly_Score"].abs() >= threshold) | (result["Rolling_Std"] == 0)
    )

    return result


def detect_rising_trend_signal(
    current_value: float,
    forecast: pd.Series,
    min_total_increase: float = 5.0,
    min_positive_ratio: float = 0.75,
) -> dict:
    """
    Gelecek tahminlerinde belirgin ve devamlı bir yükseliş
    olup olmadığını kontrol eder.

    Parameters
    ----------
    current_value : float
        Son gerçek gözlenen trend skoru.

    forecast : pd.Series
        Gelecek dönem tahminleri.

    min_total_increase : float, default=5.0
        Son tahmin değerinin mevcut değerden en az
        kaç puan yüksek olması gerektiğini belirler.

    min_positive_ratio : float, default=0.75
        Haftalık değişimlerin en az ne kadarının
        pozitif olması gerektiğini belirler.

        Örneğin 0.75:
        değişimlerin en az %75'i pozitif olmalıdır.

    Returns
    -------
    dict
        Yükselen trend sinyali ve hesaplanan
        yardımcı metrikleri içerir.
    """

    # --------------------------------------------------
    # Forecast'un son değerini alma
    # --------------------------------------------------

    forecast_end_value = float(forecast.iloc[-1])

    # --------------------------------------------------
    # Toplam beklenen değişim
    # --------------------------------------------------

    # Örneğin:
    #
    # mevcut = 70
    # 4 hafta sonrası = 76
    #
    # total_increase = 6
    total_increase = forecast_end_value - current_value

    # --------------------------------------------------
    # Haftalık tahmin değişimleri
    # --------------------------------------------------

    # Mevcut gerçek değeri forecast'un başına ekliyoruz.
    #
    # Böylece ilk tahmin haftasının da mevcut değere
    # göre artıp artmadığını hesaplayabiliriz.
    forecast_values = [
        current_value,
        *forecast.astype(float).tolist(),
    ]

    # np.diff():
    #
    # Ardışık değerler arasındaki farkları hesaplar.
    #
    # Örneğin:
    #
    # [70, 72, 74, 75]
    #
    # sonucunda:
    #
    # [2, 2, 1]
    #
    # elde edilir.
    weekly_changes = np.diff(forecast_values)

    # --------------------------------------------------
    # Pozitif haftaların oranı
    # --------------------------------------------------

    # weekly_changes > 0:
    #
    # Artan haftalara True,
    # artmayan haftalara False verir.
    #
    # .mean():
    # True = 1 ve False = 0 gibi davranabildiği için
    # pozitif haftaların oranını hesaplamış oluruz.
    positive_ratio = float((weekly_changes > 0).mean())

    # Ortalama haftalık değişim.
    average_weekly_change = float(weekly_changes.mean())

    # --------------------------------------------------
    # Final early-warning kararı
    # --------------------------------------------------

    # Yükselen trend sinyali için iki koşul istiyoruz:
    #
    # 1. Forecast sonunda toplam yükseliş
    #    en az 5 puan olmalı.
    #
    # 2. Haftalık hareketlerin en az %75'i
    #    yukarı yönlü olmalı.
    #
    # Böylece sadece tek haftalık ani bir sıçrama
    # "yükselen trend" olarak kabul edilmez.
    is_rising_signal = (
        total_increase >= min_total_increase and positive_ratio >= min_positive_ratio
    )

    # Birden fazla sonucu fonksiyondan döndürmek
    # istediğimiz için dictionary kullanıyoruz.
    return {
        "is_rising_signal": bool(is_rising_signal),
        "total_increase": float(total_increase),
        "positive_ratio": positive_ratio,
        "average_weekly_change": (average_weekly_change),
    }
