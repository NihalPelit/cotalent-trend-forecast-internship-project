# --------------------------------------------------
# Final forecasting pipeline
# --------------------------------------------------

# json:
# Model metadata dosyasını okumak için kullanıyoruz.
import json


# Path:
# Dosya yollarını daha güvenli şekilde yönetmek için.
from pathlib import Path


# NumPy:
# Tahminleri Google Trends'in 0-100
# aralığında tutmak için kullanılacak.
import numpy as np


# Pandas:
# Zaman serileri, gelecek tarihler ve
# final forecast DataFrame'i için kullanılıyor.
import pandas as pd


# Prophet modelini JSON dosyasından
# tekrar oluşturmak için kullanıyoruz.
from prophet.serialize import model_from_json


# Kaydedilmiş XGBoost modelini
# yeniden yüklemek için kullanıyoruz.
from xgboost import XGBRegressor


def load_model_metadata(
    metadata_path: str | Path,
) -> dict:
    """
    Final model metadata JSON dosyasını yükler.

    Parameters
    ----------
    metadata_path : str | Path
        Model konfigürasyon bilgilerini içeren metadata JSON dosyasının yolu.

    Returns
    -------
    dict
        JSON dosyasından okunan model konfigürasyon bilgilerini içeren
        Python dictionary nesnesi.
    """

    # Gelen yolu Path nesnesine dönüştürüyoruz.
    #
    # Böylece ister string ister Path verilmiş olsun
    # aynı şekilde çalışabiliriz.
    metadata_path = Path(metadata_path)

    # JSON dosyasını okuma modunda açıyoruz.
    with open(
        metadata_path,
        "r",
        encoding="utf-8",
    ) as file:
        # json.load():
        # JSON dosyasını Python dictionary'sine çevirir.
        metadata = json.load(file)

    return metadata


def load_prophet_model(
    model_path: str | Path,
):
    """
    Kaydedilmiş Prophet modelini JSON dosyasından yükler.

    Parameters
    ----------
    model_path : str | Path
        Prophet modelinin JSON formatında kaydedildiği dosyanın yolu.

    Returns
    -------
    object
        JSON içeriğinden yeniden oluşturulmuş, önceden eğitilmiş
        Prophet model nesnesi.

    Notes
    -----
    Model, Prophet'in `model_from_json()` serialization mekanizması
    kullanılarak yeniden oluşturulur.
    """

    # Dosya yolunu Path nesnesine çeviriyoruz.
    model_path = Path(model_path)

    # Prophet JSON dosyasını metin olarak okuyoruz.
    with open(
        model_path,
        "r",
        encoding="utf-8",
    ) as file:
        model_json = file.read()

    # model_from_json():
    # JSON içeriğini tekrar eğitilmiş
    # Prophet model nesnesine dönüştürür.
    model = model_from_json(model_json)

    return model


def load_xgb_model(
    model_path: str | Path,
) -> XGBRegressor:
    """
    Kaydedilmiş XGBoost modelini dosyadan yükler.

    Parameters
    ----------
    model_path : str | Path
        `save_model()` ile kaydedilmiş XGBoost model dosyasının yolu.

    Returns
    -------
    XGBRegressor
        Dosyadan yeniden yüklenmiş, önceden eğitilmiş XGBoost model nesnesi.

    Notes
    -----
    Önce boş bir `XGBRegressor` nesnesi oluşturulur, ardından
    `load_model()` ile kaydedilmiş model parametreleri ve öğrenilmiş
    ağaç yapısı yüklenir.
    """

    model_path = Path(model_path)

    # Önce boş bir XGBRegressor oluşturuyoruz.
    model = XGBRegressor()

    # Daha önce save_model() ile kaydettiğimiz
    # öğrenilmiş ağaçları bu nesnenin içine yüklüyoruz.
    model.load_model(str(model_path))

    return model


def forecast_prophet_loaded(
    model,
    series: pd.Series,
    steps: int,
    clip_range: tuple[float, float] | None = (0, 100),
) -> pd.Series:
    """
    Önceden eğitilmiş Prophet modeliyle gelecek tahmini üretir.

    Parameters
    ----------
    model : object
        Daha önce eğitilmiş ve diskten yüklenmiş Prophet model nesnesi.

    series : pd.Series
        Son gözlem tarihini ve geçmiş zaman serisini içeren veri.
        Gelecek tahmin tarihlerinin başlangıcı bu serinin son tarihine
        göre belirlenir.

    steps : int
        Gelecekte tahmin edilecek hafta sayısı.

    clip_range : tuple[float, float] | None, default=(0, 100)
        Tahminlerin tutulacağı alt ve üst sınır. `None` verilirse
        clipping işlemi uygulanmaz.

    Returns
    -------
    pd.Series
        Gelecek haftalara ait Prophet tahminleri. Serinin index'i
        haftalık (`W-SUN`) gelecek tarihlerden oluşur.

    Notes
    -----
    Bu fonksiyon modeli yeniden eğitmez. Yalnızca önceden eğitilmiş
    Prophet modelinin `predict()` metodunu kullanarak inference yapar.
    """

    # --------------------------------------------------
    # Gelecek tarihleri oluşturma
    # --------------------------------------------------

    # Son gerçek gözlemden 1 hafta sonrasından
    # başlayarak yeni Pazar tarihleri oluşturuyoruz.
    future_dates = pd.date_range(
        start=(series.index[-1] + pd.Timedelta(weeks=1)),
        periods=steps,
        freq="W-SUN",
    )

    # Prophet predict() fonksiyonu
    # "ds" isimli tarih sütunu bekler.
    future_df = pd.DataFrame({"ds": future_dates})

    # --------------------------------------------------
    # Tahmin üretme
    # --------------------------------------------------

    forecast = model.predict(future_df)

    # yhat:
    # Prophet'in ana tahmin değeridir.
    predictions = forecast["yhat"].to_numpy()

    # --------------------------------------------------
    # Google Trends sınırı
    # --------------------------------------------------

    # Google Trends değerleri doğal olarak
    # 0-100 arasında olduğu için gerekli olduğunda
    # tahminleri bu aralıkta tutuyoruz.
    if clip_range is not None:
        predictions = np.clip(
            predictions,
            clip_range[0],
            clip_range[1],
        )

    # Tarihli pandas Series olarak döndürüyoruz.
    return pd.Series(
        predictions,
        index=future_dates,
        name="prophet_forecast",
    )


def forecast_xgb_loaded(
    model: XGBRegressor,
    series: pd.Series,
    steps: int,
    n_lags: int = 8,
    clip_range: tuple[float, float] | None = (0, 100),
) -> pd.Series:
    """
    Önceden eğitilmiş XGBoost modeliyle recursive gelecek tahmini üretir.

    Parameters
    ----------
    model : XGBRegressor
        Daha önce eğitilmiş ve diskten yüklenmiş XGBoost model nesnesi.

    series : pd.Series
        Recursive forecasting için başlangıç geçmişini sağlayan tarihsel
        zaman serisi.

    steps : int
        Gelecekte tahmin edilecek hafta sayısı.

    n_lags : int, default=8
        Modelin her tahmin adımında kullanacağı geçmiş dönem sayısı.

    clip_range : tuple[float, float] | None, default=(0, 100)
        Tahminlerin tutulacağı alt ve üst sınır. `None` verilirse
        clipping işlemi uygulanmaz.

    Returns
    -------
    pd.Series
        Gelecek haftalara ait recursive XGBoost tahminleri. Serinin
        index'i haftalık (`W-SUN`) gelecek tarihlerden oluşur.

    Notes
    -----
    Model `lag_1 ... lag_n`, `change_1` ve `change_2` feature'larını
    kullanır. Her tahmin bir sonraki adımda geçmişe eklenerek yeni
    `lag_1` değerinin oluşmasını sağlar.
    """

    # Modelde kullanılan feature isimlerini
    # training sırasında kullandığımız sırayla oluşturuyoruz.
    feature_columns = [
        *[
            f"lag_{i}"
            for i in range(
                1,
                n_lags + 1,
            )
        ],
        "change_1",
        "change_2",
    ]

    # Geçmiş gerçek değerleri liste haline getiriyoruz.
    #
    # Daha sonra ürettiğimiz tahminler de bu listenin
    # sonuna eklenecek.
    history = series.astype(float).tolist()

    predictions = []

    # --------------------------------------------------
    # Recursive forecasting
    # --------------------------------------------------

    for _ in range(steps):
        # En yakın geçmişten başlayarak
        # son n_lags haftayı alıyoruz.
        #
        # lags[0] -> lag_1
        # lags[1] -> lag_2
        # ...
        lags = [
            history[-i]
            for i in range(
                1,
                n_lags + 1,
            )
        ]

        # Lag feature'larını dictionary olarak oluşturuyoruz.
        feature_row = {f"lag_{i + 1}": lags[i] for i in range(n_lags)}

        # Son haftalık değişim.
        feature_row["change_1"] = lags[0] - lags[1]

        # Ondan önceki haftalık değişim.
        feature_row["change_2"] = lags[1] - lags[2]

        # Model tek satırlık DataFrame üzerinden
        # gelecek haftayı tahmin edecek.
        X_future = pd.DataFrame(
            [feature_row],
            columns=feature_columns,
        )

        prediction = float(model.predict(X_future)[0])

        # Google Trends sınırı uygulanıyor.
        if clip_range is not None:
            prediction = float(
                np.clip(
                    prediction,
                    clip_range[0],
                    clip_range[1],
                )
            )

        predictions.append(prediction)

        # Recursive forecasting:
        #
        # Bu tahmin bir sonraki haftanın
        # lag_1 değeri haline geliyor.
        history.append(prediction)

    # --------------------------------------------------
    # Gelecek tarihleri oluşturma
    # --------------------------------------------------

    future_dates = pd.date_range(
        start=(series.index[-1] + pd.Timedelta(weeks=1)),
        periods=steps,
        freq="W-SUN",
    )

    return pd.Series(
        predictions,
        index=future_dates,
        name="xgb_forecast",
    )


def forecast_naive_loaded(
    series: pd.Series,
    steps: int,
) -> pd.Series:
    """
    Son gözlenen değeri gelecek dönemlere taşıyan Naive forecast üretir.

    Parameters
    ----------
    series : pd.Series
        Son gözlenen değeri ve son tarihi içeren tarihsel zaman serisi.

    steps : int
        Gelecekte tahmin edilecek hafta sayısı.

    Returns
    -------
    pd.Series
        Son gözlenen değerin tüm forecast horizonuna tekrarlandığı
        Naive tahmin serisi. Index haftalık (`W-SUN`) gelecek tarihlerden
        oluşur.

    Notes
    -----
    Naive yöntem model eğitimi gerektirmez; serinin son gerçek değerini
    bütün gelecek dönemler için sabit tahmin olarak kullanır.
    """

    # Zaman serisinin en son gerçek değerini alıyoruz.
    last_value = float(series.iloc[-1])

    # Gelecek haftaların tarihlerini oluşturuyoruz.
    future_dates = pd.date_range(
        start=(series.index[-1] + pd.Timedelta(weeks=1)),
        periods=steps,
        freq="W-SUN",
    )

    # Bütün gelecek haftalara aynı son değeri veriyoruz.
    return pd.Series(
        last_value,
        index=future_dates,
        name="naive_forecast",
    )


def generate_final_forecast(
    data: pd.DataFrame,
    models_dir: str | Path,
    metadata_path: str | Path,
) -> pd.DataFrame:
    """
    Kaydedilmiş final modelleri ve metadata bilgilerini kullanarak
    ChatGPT, Gemini ve Claude için final gelecek tahminlerini üretir.

    Parameters
    ----------
    data : pd.DataFrame
        `chatgpt`, `gemini` ve `claude` sütunlarını içeren, tarih index'li
        güncel Google Trends veri seti.

    models_dir : str | Path
        Kaydedilmiş Prophet ve XGBoost model dosyalarının bulunduğu
        klasörün yolu.

    metadata_path : str | Path
        Final model seçimlerini, model dosya adlarını, ensemble
        ağırlıklarını, lag sayısını, forecast horizonunu ve veri cutoff
        tarihini içeren metadata JSON dosyasının yolu.

    Returns
    -------
    pd.DataFrame
        ChatGPT, Gemini ve Claude için final gelecek tahminlerini içeren
        tarih index'li DataFrame.

    Raises
    ------
    ValueError
        Veri setinin son tarihi ile metadata içerisinde kayıtlı
        `data_cutoff_date` eşleşmediğinde yükseltilir.

    Notes
    -----
    ChatGPT tahmini, metadata'da kayıtlı ağırlıklarla Prophet ve XGBoost
    tahminlerinin ensemble edilmesiyle oluşturulur. Gemini ve Claude
    tahminleri ise mevcut final model seçimine göre Naive yöntemle
    üretilir. Bu fonksiyon kaydedilmiş modelleri yeniden eğitmez.
    """

    # --------------------------------------------------
    # Dosya yollarını hazırlama
    # --------------------------------------------------

    models_dir = Path(models_dir)

    metadata_path = Path(metadata_path)

    # --------------------------------------------------
    # Metadata'yı yükleme
    # --------------------------------------------------

    metadata = load_model_metadata(metadata_path)

    # Metadata içinde kaç haftalık forecast
    # üretileceği kayıtlı.
    steps = metadata["forecast_horizon_weeks"]

    # --------------------------------------------------
    # Veri tarihi kontrolü
    # --------------------------------------------------

    # Elimizdeki DataFrame'in son tarihini alıyoruz.
    current_data_date = data.index[-1].strftime("%Y-%m-%d")

    # Modellerin eğitildiği veri kesim tarihini
    # metadata'dan okuyoruz.
    model_data_date = metadata["data_cutoff_date"]

    # Eğer modele yeni veri vermeye çalışırsak
    # burada duruyoruz.
    #
    # Çünkü kaydedilmiş modeller eski veriyle
    # eğitilmiş olabilir.
    if current_data_date != model_data_date:
        raise ValueError(
            "Veri tarihi ile model metadata tarihi eşleşmiyor. "
            "Modellerin yeniden eğitilmesi gerekebilir."
        )

    # --------------------------------------------------
    # ChatGPT modellerini yükleme
    # --------------------------------------------------

    # Prophet model dosyasının adını metadata'dan alıyoruz.
    prophet_file = metadata["chatgpt"]["prophet"]["model_file"]

    # XGBoost model dosyasının adını metadata'dan alıyoruz.
    xgb_file = metadata["chatgpt"]["xgboost"]["model_file"]

    # Diskten iki modeli yüklüyoruz.
    prophet_model = load_prophet_model(models_dir / prophet_file)

    xgb_model = load_xgb_model(models_dir / xgb_file)

    # --------------------------------------------------
    # ChatGPT tahminleri
    # --------------------------------------------------

    chatgpt_series = data["chatgpt"]

    prophet_forecast = forecast_prophet_loaded(
        model=prophet_model,
        series=chatgpt_series,
        steps=steps,
    )

    # n_lags değerini de metadata'dan okuyoruz.
    n_lags = metadata["chatgpt"]["xgboost"]["n_lags"]

    xgb_forecast = forecast_xgb_loaded(
        model=xgb_model,
        series=chatgpt_series,
        steps=steps,
        n_lags=n_lags,
    )

    # --------------------------------------------------
    # Ensemble ağırlıkları
    # --------------------------------------------------

    prophet_weight = metadata["chatgpt"]["weights"]["prophet"]

    xgb_weight = metadata["chatgpt"]["weights"]["xgboost"]

    # Final ChatGPT tahmini:
    #
    # 0.5 Prophet + 0.5 XGBoost
    chatgpt_forecast = prophet_weight * prophet_forecast + xgb_weight * xgb_forecast

    # --------------------------------------------------
    # Gemini - Naive
    # --------------------------------------------------

    gemini_forecast = forecast_naive_loaded(
        series=data["gemini"],
        steps=steps,
    )

    # --------------------------------------------------
    # Claude - Naive
    # --------------------------------------------------

    claude_forecast = forecast_naive_loaded(
        series=data["claude"],
        steps=steps,
    )

    # --------------------------------------------------
    # Final forecast tablosu
    # --------------------------------------------------

    final_forecast = pd.DataFrame(
        {
            "ChatGPT": chatgpt_forecast,
            "Gemini": gemini_forecast,
            "Claude": claude_forecast,
        }
    )

    # Index'e anlamlı bir isim veriyoruz.
    final_forecast.index.name = "Date"

    return final_forecast
