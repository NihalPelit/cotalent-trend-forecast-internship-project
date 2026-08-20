import pandas as pd
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


def decompose_series(
    series: pd.Series,
    period: int = 52,
    model: str = "additive",
) -> DecomposeResult:
    """
    Bir zaman serisini trend, seasonal ve residual bileşenlerine ayırır.

    Parameters
    ----------
    series : pd.Series
        Decomposition uygulanacak tarihsel zaman serisi.

    period : int, default=52
        Mevsimsel döngünün kaç gözlemde bir tekrar ettiğini belirtir.
        Haftalık veride 52 değeri yaklaşık bir yıllık sezonsallığı
        temsil eder.

    model : str, default="additive"
        Kullanılacak decomposition modelinin türü.
        Bu projede varsayılan olarak additive yapı kullanılmaktadır.

    Returns
    -------
    DecomposeResult
        `observed`, `trend`, `seasonal` ve `resid` bileşenlerini içeren
        statsmodels decomposition sonuç nesnesi.

    Notes
    -----
    Fonksiyon, statsmodels içerisindeki `seasonal_decompose()` metodunu
    kullanır. `period=52` seçimi, haftalık Google Trends serisinde
    yaklaşık yıllık bir döngüyü temsil etmek amacıyla kullanılır.
    """

    decomposition = seasonal_decompose(
        series,
        model=model,
        period=period,
    )

    return decomposition


def decomposition_to_dataframe(
    decomposition: DecomposeResult,
) -> pd.DataFrame:
    """
    Decomposition sonucunu analiz edilebilir bir DataFrame'e dönüştürür.

    Parameters
    ----------
    decomposition : DecomposeResult
        `seasonal_decompose()` veya `decompose_series()` tarafından
        üretilmiş decomposition sonuç nesnesi.

    Returns
    -------
    pd.DataFrame
        `observed`, `trend`, `seasonal`, `residual` ve `expected`
        sütunlarını içeren decomposition tablosu.

    Notes
    -----
    `expected` sütunu additive decomposition yapısına uygun olarak
    `trend + seasonal` toplamından oluşturulur.

    Residual bileşen ise gözlenen değerin bu beklenen yapıdan ne kadar
    saptığını incelemek için kullanılabilir.
    """

    data = pd.DataFrame(
        {
            "observed": decomposition.observed,
            "trend": decomposition.trend,
            "seasonal": decomposition.seasonal,
            "residual": decomposition.resid,
        }
    )

    data["expected"] = data["trend"] + data["seasonal"]

    return data
