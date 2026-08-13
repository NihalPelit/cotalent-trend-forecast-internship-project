import time

import pandas as pd
from pytrends.exceptions import ResponseError, TooManyRequestsError
from pytrends.request import TrendReq


def fetch_trends_data(
    keywords: list[str],
    geo: str = "TR",
    timeframe: str = "today 5-y",
    max_retries: int = 2,
    backoff_seconds: int = 30,
) -> pd.DataFrame:
    """
    Google Trends'ten zaman serisi ilgi verisi çeker.

    Args:
        keywords: Aranacak kelimelerin listesi.
        geo: Google Trends ülke kodu.
        timeframe: Verinin çekileceği zaman aralığı.
        max_retries: 429 hatasında yapılacak ek deneme sayısı.
        backoff_seconds: Yeniden denemeden önce beklenecek temel süre.

    Returns:
        Google Trends zaman serisini içeren DataFrame.

    Raises:
        ValueError: Keyword listesi boş olduğunda.
        TypeError: Keyword listesindeki bir değer string olmadığında.
        RuntimeError: Google Trends isteği başarısız olduğunda.
    """

    if not keywords:
        raise ValueError("Keyword listesi boş olamaz.")

    if not all(isinstance(keyword, str) for keyword in keywords):
        raise TypeError("Tüm keyword değerleri string olmalıdır.")

    for attempt in range(max_retries + 1):
        try:
            pytrend = TrendReq(
                hl="tr-TR",
                tz=180,
            )

            pytrend.build_payload(
                kw_list=keywords,
                timeframe=timeframe,
                geo=geo,
            )

            data = pytrend.interest_over_time()

            return data

        except TooManyRequestsError as error:
            if attempt == max_retries:
                raise RuntimeError(
                    "Google Trends 429 Too Many Requests hatası vermeye "
                    "devam ediyor. Daha sonra tekrar deneyin."
                ) from error

            wait_time = backoff_seconds * (2**attempt)

            print(f"429 hatası alındı. {wait_time} saniye sonra tekrar denenecek.")

            time.sleep(wait_time)

        except ResponseError as error:
            print("ResponseError type:", type(error).__name__)
            print("ResponseError detail:", error)

            raise RuntimeError(
                "Google Trends isteği başarısız oldu. "
                "İstek parametrelerini veya pytrends uyumluluğunu kontrol edin."
            ) from error
