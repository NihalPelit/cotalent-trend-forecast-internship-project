import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor


def clip_predictions(
    predictions,
    clip_range: tuple[float, float] | None = None,
):
    """
    Tahmin değerlerini belirtilen alt ve üst sınırlar arasında tutar.

    Parameters
    ----------
    predictions : array-like
        Sınırlandırılacak tahmin değerleri.

    clip_range : tuple[float, float] | None, default=None
        Tahminlerin tutulacağı alt ve üst sınır. `None` verilirse
        tahmin değerlerine herhangi bir clipping işlemi uygulanmaz.

    Returns
    -------
    array-like
        Belirtilen aralığa göre sınırlandırılmış tahmin değerleri.
        `clip_range=None` ise orijinal tahminler döndürülür.

    Notes
    -----
    Google Trends verileri doğal olarak 0 ile 100 arasında olduğu için
    bu projede gerektiğinde `clip_range=(0, 100)` kullanılmaktadır.
    """

    if clip_range is None:
        return predictions

    return np.clip(
        predictions,
        clip_range[0],
        clip_range[1],
    )


def evaluate_naive_cv(
    series: pd.Series,
    splitter: TimeSeriesSplit,
) -> pd.DataFrame:
    """
    Naive modeli time-series cross-validation ile değerlendirir.

    Parameters
    ----------
    series : pd.Series
        Değerlendirilecek tarihsel zaman serisi.

    splitter : TimeSeriesSplit
        Zaman sırasını koruyarak train ve test fold'larını oluşturan
        scikit-learn `TimeSeriesSplit` nesnesi.

    Returns
    -------
    pd.DataFrame
        Her cross-validation fold'u için fold numarası, MAE ve RMSE
        değerlerini içeren sonuç tablosu.

    Notes
    -----
    Naive tahminde her test döneminin tahmini, ilgili train dönemindeki
    son gözlenen değerin test horizonunun tamamına tekrar edilmesiyle
    oluşturulur.
    """

    results = []

    for fold, (train_index, test_index) in enumerate(
        splitter.split(series),
        start=1,
    ):
        train = series.iloc[train_index]
        test = series.iloc[test_index]

        last_value = train.iloc[-1]

        prediction = pd.Series(
            last_value,
            index=test.index,
        )

        mae = mean_absolute_error(
            test,
            prediction,
        )

        rmse = root_mean_squared_error(
            test,
            prediction,
        )

        results.append(
            {
                "fold": fold,
                "MAE": mae,
                "RMSE": rmse,
            }
        )

    return pd.DataFrame(results)


def forecast_naive(
    series: pd.Series,
    steps: int,
) -> pd.Series:
    """
    Son gözlenen değeri gelecek dönemler için tahmin olarak kullanır.

    Parameters
    ----------
    series : pd.Series
        Gelecek tahmini üretilecek tarihsel zaman serisi.

    steps : int
        Gelecekte tahmin edilecek hafta sayısı.

    Returns
    -------
    pd.Series
        Gelecek haftalara ait Naive tahminleri. Serinin index'i
        haftalık (`W-SUN`) gelecek tarihlerden oluşur.

    Notes
    -----
    Naive yöntem, serideki son gerçek değeri tüm forecast horizonunda
    sabit tahmin olarak kullanır.
    """

    last_value = series.iloc[-1]

    future_index = pd.date_range(
        start=series.index[-1] + pd.Timedelta(weeks=1),
        periods=steps,
        freq="W-SUN",
    )

    predictions = pd.Series(
        last_value,
        index=future_index,
        name="naive_forecast",
    )

    return predictions


def evaluate_arima_cv(
    series: pd.Series,
    splitter: TimeSeriesSplit,
    order: tuple[int, int, int],
    clip_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """
    ARIMA modelini time-series cross-validation ile değerlendirir.

    Parameters
    ----------
    series : pd.Series
        Değerlendirilecek tarihsel zaman serisi.

    splitter : TimeSeriesSplit
        Zaman sırasını koruyarak train ve test fold'larını oluşturan
        scikit-learn `TimeSeriesSplit` nesnesi.

    order : tuple[int, int, int]
        ARIMA modelinin `(p, d, q)` parametreleri.

    clip_range : tuple[float, float] | None, default=None
        Tahminlerin tutulacağı alt ve üst sınır. `None` ise clipping
        uygulanmaz.

    Returns
    -------
    pd.DataFrame
        Her cross-validation fold'u için fold numarası, MAE ve RMSE
        değerlerini içeren sonuç tablosu.

    Notes
    -----
    Her fold'da ARIMA modeli yalnızca train bölümünde eğitilir ve test
    horizonunun tamamı için ileri tahmin üretir.
    """

    results = []

    for fold, (train_index, test_index) in enumerate(
        splitter.split(series),
        start=1,
    ):
        train = series.iloc[train_index]
        test = series.iloc[test_index]

        model = ARIMA(
            train,
            order=order,
        )

        fitted_model = model.fit()

        prediction = fitted_model.forecast(steps=len(test))

        if clip_range is not None:
            prediction = prediction.clip(
                lower=clip_range[0],
                upper=clip_range[1],
            )

        mae = mean_absolute_error(
            test,
            prediction,
        )

        rmse = root_mean_squared_error(
            test,
            prediction,
        )

        results.append(
            {
                "fold": fold,
                "MAE": mae,
                "RMSE": rmse,
            }
        )

    return pd.DataFrame(results)


def forecast_arima(
    series: pd.Series,
    order: tuple[int, int, int],
    steps: int,
) -> pd.Series:
    """
    ARIMA modelini tüm seri üzerinde eğitir ve ileri tahmin üretir.

    Parameters
    ----------
    series : pd.Series
        Modelin eğitileceği tarihsel zaman serisi.

    order : tuple[int, int, int]
        ARIMA modelinin `(p, d, q)` parametreleri.

    steps : int
        Gelecekte tahmin edilecek dönem sayısı.

    Returns
    -------
    pd.Series
        Eğitilmiş ARIMA modelinin gelecek dönem tahminleri.
    """

    model = ARIMA(
        series,
        order=order,
    )

    fitted_model = model.fit()

    prediction = fitted_model.forecast(steps=steps)

    return prediction


def evaluate_prophet_cv(
    series: pd.Series,
    splitter: TimeSeriesSplit,
    changepoint_prior_scale: float = 1.0,
    yearly_seasonality=True,
    clip_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """
    Prophet modelini time-series cross-validation ile değerlendirir.

    Parameters
    ----------
    series : pd.Series
        Değerlendirilecek tarihsel zaman serisi.

    splitter : TimeSeriesSplit
        Zaman sırasını koruyarak train ve test fold'larını oluşturan
        scikit-learn `TimeSeriesSplit` nesnesi.

    changepoint_prior_scale : float, default=1.0
        Prophet modelinin trend değişimlerine ne kadar esnek tepki
        vereceğini belirleyen parametre.

    yearly_seasonality : str | bool, default=True
        Prophet modelinde yıllık sezonsallığın kullanım biçimi.

    clip_range : tuple[float, float] | None, default=None
        Tahminlerin tutulacağı alt ve üst sınır. `None` ise clipping
        uygulanmaz.

    Returns
    -------
    pd.DataFrame
        Her cross-validation fold'u için fold numarası, MAE ve RMSE
        değerlerini içeren sonuç tablosu.

    Notes
    -----
    Her fold'da Prophet modeli yalnızca train verisiyle eğitilir ve
    test tarihlerine karşılık gelen tahminler üzerinden değerlendirilir.
    """

    results = []

    for fold, (train_index, test_index) in enumerate(
        splitter.split(series),
        start=1,
    ):
        train = series.iloc[train_index]
        test = series.iloc[test_index]

        train_df = train.rename("y").reset_index().rename(columns={"date": "ds"})

        test_df = test.rename("y").reset_index().rename(columns={"date": "ds"})

        model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=changepoint_prior_scale,
        )

        model.fit(train_df)

        forecast = model.predict(test_df[["ds"]])

        prediction = clip_predictions(
            forecast["yhat"].to_numpy(),
            clip_range,
        )

        mae = mean_absolute_error(
            test_df["y"],
            prediction,
        )

        rmse = root_mean_squared_error(
            test_df["y"],
            prediction,
        )

        results.append(
            {
                "fold": fold,
                "MAE": mae,
                "RMSE": rmse,
            }
        )

    return pd.DataFrame(results)


def train_prophet_model(
    series: pd.Series,
    changepoint_prior_scale: float = 1.0,
    yearly_seasonality: str | bool = "auto",
) -> Prophet:
    """
    Prophet modelini verilen zaman serisinin tamamı üzerinde eğitir.

    Parameters
    ----------
    series : pd.Series
        Eğitilecek tarihsel zaman serisi.

    changepoint_prior_scale : float, default=1.0
        Prophet modelinin trend değişimlerine ne kadar esnek tepki
        vereceğini belirler.

    yearly_seasonality : str | bool, default="auto"
        Yıllık sezonsallığın kullanım biçimini belirler.

    Returns
    -------
    Prophet
        Verilen serinin tamamı üzerinde eğitilmiş Prophet model nesnesi.

    Notes
    -----
    Fonksiyon tarih index'ini Prophet'in beklediği `ds` sütununa,
    seri değerlerini ise `y` sütununa dönüştürerek modeli eğitir.
    """

    # --------------------------------------------------
    # Prophet veri formatını hazırlama
    # --------------------------------------------------

    # Prophet iki özel sütun bekler:
    #
    # ds -> tarih
    # y  -> tahmin edilmeye çalışılan değer
    #
    # Bizim serimizde tarih index durumunda olduğu için
    # reset_index() ile normal sütuna çeviriyoruz.
    data = series.rename("y").reset_index().rename(columns={"date": "ds"})

    # --------------------------------------------------
    # Prophet modelini oluşturma
    # --------------------------------------------------

    model = Prophet(
        # Daha önce model karşılaştırmalarında kullandığımız
        # yearly seasonality ayarını koruyoruz.
        yearly_seasonality=yearly_seasonality,
        # Verimiz haftalık olduğu için Prophet'in
        # kendi weekly seasonality özelliğini kullanmıyoruz.
        weekly_seasonality=False,
        # Günlük veri kullanmadığımız için
        # daily seasonality de kapalı.
        daily_seasonality=False,
        # Daha önce tuning sonucunda seçtiğimiz
        # trend esnekliği parametresi.
        changepoint_prior_scale=changepoint_prior_scale,
    )

    # --------------------------------------------------
    # Modeli eğitme
    # --------------------------------------------------

    # Verilen serinin tamamını kullanarak
    # Prophet modelini eğitiyoruz.
    model.fit(data)

    # Tahmin sonucu değil,
    # eğitilmiş model nesnesini döndürüyoruz.
    #
    # Day 11'de bu nesneyi models/ klasörüne
    # kaydedebilmemiz için buna ihtiyacımız var.
    return model


def forecast_prophet(
    series: pd.Series,
    steps: int,
    changepoint_prior_scale: float = 1.0,
    yearly_seasonality: str | bool = "auto",
) -> pd.DataFrame:
    """
    Prophet modelini tüm seri üzerinde eğitir ve ileriye yönelik tahmin üretir.

    Parameters
    ----------
    series : pd.Series
        Gelecek tahmini üretilecek tarihsel zaman serisi.

    steps : int
        Gelecekte tahmin edilecek hafta sayısı.

    changepoint_prior_scale : float, default=1.0
        Prophet modelinin trend değişimlerine ne kadar esnek tepki
        vereceğini belirler.

    yearly_seasonality : str | bool, default="auto"
        Yıllık sezonsallığın kullanım biçimini belirler.

    Returns
    -------
    pd.DataFrame
        Gelecek `steps` dönem için `ds`, `yhat`, `yhat_lower` ve
        `yhat_upper` sütunlarını içeren Prophet tahmin tablosu.

    Notes
    -----
    Model eğitimi `train_prophet_model()` fonksiyonu üzerinden yapılır.
    Gelecek tarihler haftalık `W-SUN` frekansıyla oluşturulur.
    """

    # --------------------------------------------------
    # Prophet modelini eğitme
    # --------------------------------------------------

    # Model oluşturma ve fit işlemini artık
    # train_prophet_model() fonksiyonuna bırakıyoruz.
    #
    # Böylece aynı training kodunu iki farklı
    # yerde tekrar etmiyoruz.
    model = train_prophet_model(
        series=series,
        changepoint_prior_scale=changepoint_prior_scale,
        yearly_seasonality=yearly_seasonality,
    )

    # --------------------------------------------------
    # Gelecek tarihleri oluşturma
    # --------------------------------------------------

    # periods=steps:
    # kaç gelecek hafta tahmin edeceğimizi belirler.
    #
    # freq="W-SUN":
    # haftalık verimizin Pazar tarihli yapısını korur.
    future = model.make_future_dataframe(
        periods=steps,
        freq="W-SUN",
    )

    # --------------------------------------------------
    # Tahmin oluşturma
    # --------------------------------------------------

    forecast = model.predict(future)

    # Sadece gelecekteki "steps" kadar satırı
    # ve ihtiyacımız olan sütunları döndürüyoruz.
    return forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
        ]
    ].tail(steps)


def evaluate_xgb_recursive_with_change(
    X: pd.DataFrame,
    y: pd.Series,
    splitter: TimeSeriesSplit,
    n_lags: int = 8,
    max_depth: int = 2,
    n_estimators: int = 300,
    learning_rate: float = 0.03,
    clip_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """
    XGBoost modelini recursive time-series cross-validation ile değerlendirir.

    Parameters
    ----------
    X : pd.DataFrame
        Lag ve change feature'larını içeren model girdi tablosu.

    y : pd.Series
        Modelin tahmin etmeye çalıştığı hedef zaman serisi.

    splitter : TimeSeriesSplit
        Zaman sırasını koruyarak train ve test fold'larını oluşturan
        scikit-learn `TimeSeriesSplit` nesnesi.

    n_lags : int, default=8
        Recursive tahminde kullanılacak geçmiş dönem sayısı.

    max_depth : int, default=2
        XGBoost ağaçlarının maksimum derinliği.

    n_estimators : int, default=300
        Kullanılacak boosting ağacı sayısı.

    learning_rate : float, default=0.03
        Her ağacın modele katkısının büyüklüğünü belirleyen öğrenme oranı.

    clip_range : tuple[float, float] | None, default=None
        Tahminlerin tutulacağı alt ve üst sınır. `None` ise clipping
        uygulanmaz.

    Returns
    -------
    pd.DataFrame
        Her cross-validation fold'u için fold numarası, MAE ve RMSE
        değerlerini içeren sonuç tablosu.

    Notes
    -----
    Tahminler recursive olarak üretilir. Bir adımda üretilen tahmin,
    sonraki adımın lag girdileri arasına eklenir. Böylece test dönemindeki
    gerçek gelecek değerleri modele girdi olarak verilmez.
    """

    results = []

    for fold, (train_index, test_index) in enumerate(
        splitter.split(X),
        start=1,
    ):
        X_train = X.iloc[train_index]
        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
        )

        model.fit(
            X_train,
            y_train,
        )

        history = list(y_train.iloc[-n_lags:])

        predictions = []

        for _ in range(len(y_test)):
            lag_features = [history[-lag] for lag in range(1, n_lags + 1)]

            change_1 = lag_features[0] - lag_features[1]

            change_2 = lag_features[1] - lag_features[2]

            features = lag_features + [
                change_1,
                change_2,
            ]

            current_features = pd.DataFrame(
                [features],
                columns=X.columns,
            )

            prediction = model.predict(current_features)[0]

            if clip_range is not None:
                prediction = float(
                    np.clip(
                        prediction,
                        clip_range[0],
                        clip_range[1],
                    )
                )

            predictions.append(prediction)

            history.append(prediction)

        mae = mean_absolute_error(
            y_test,
            predictions,
        )

        rmse = root_mean_squared_error(
            y_test,
            predictions,
        )

        results.append(
            {
                "fold": fold,
                "MAE": mae,
                "RMSE": rmse,
            }
        )

    return pd.DataFrame(results)


def train_xgb_model(
    series: pd.Series,
    n_lags: int = 8,
    max_depth: int = 2,
    n_estimators: int = 300,
    learning_rate: float = 0.03,
    random_state: int = 42,
) -> XGBRegressor:
    """
    Lag ve change feature'larını kullanarak XGBoost modelini tüm seri üzerinde eğitir.

    Parameters
    ----------
    series : pd.Series
        Eğitilecek tarihsel zaman serisi.

    n_lags : int, default=8
        Modelin kullanacağı geçmiş dönem sayısı.

    max_depth : int, default=2
        XGBoost ağaçlarının maksimum derinliği.

    n_estimators : int, default=300
        Kullanılacak toplam boosting ağacı sayısı.

    learning_rate : float, default=0.03
        Her ağacın modele katkısının büyüklüğünü belirleyen öğrenme oranı.

    random_state : int, default=42
        Model eğitimindeki rastgeleliği sabitleyerek sonuçların tekrar
        üretilebilir olmasına yardımcı olur.

    Returns
    -------
    XGBRegressor
        Lag ve change feature'ları üzerinde eğitilmiş XGBoost model nesnesi.

    Notes
    -----
    Girdi feature'ları `lag_1 ... lag_n`, `change_1` ve `change_2`
    sütunlarından oluşturulur. Lag üretimi nedeniyle oluşan eksik
    başlangıç satırları eğitimden önce kaldırılır.
    """

    # --------------------------------------------------
    # Lag feature'larını oluşturma
    # --------------------------------------------------

    # target:
    # modelin tahmin etmeye çalışacağı gerçek değer.
    #
    # lag_1 ... lag_8:
    # önceki haftaların Google Trends değerleri.
    lag_data = pd.DataFrame(
        {
            "target": series,
            # Dictionary comprehension kullanarak
            # lag_1'den lag_8'e kadar sütunları
            # otomatik oluşturuyoruz.
            **{
                f"lag_{i}": series.shift(i)
                for i in range(
                    1,
                    n_lags + 1,
                )
            },
        }
    ).dropna()

    # --------------------------------------------------
    # Change feature'larını oluşturma
    # --------------------------------------------------

    # Son haftalık değişim.
    lag_data["change_1"] = lag_data["lag_1"] - lag_data["lag_2"]

    # Ondan önceki haftalık değişim.
    lag_data["change_2"] = lag_data["lag_2"] - lag_data["lag_3"]

    # --------------------------------------------------
    # Model feature'larını belirleme
    # --------------------------------------------------

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

    # X:
    # modelin input olarak göreceği feature'lar.
    X = lag_data[feature_columns]

    # y:
    # modelin tahmin etmeyi öğreneceği gerçek değer.
    y = lag_data["target"]

    # --------------------------------------------------
    # XGBoost modelini oluşturma
    # --------------------------------------------------

    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=random_state,
    )

    # --------------------------------------------------
    # Modeli eğitme
    # --------------------------------------------------

    model.fit(
        X,
        y,
    )

    # Tahminleri değil,
    # eğitilmiş XGBoost nesnesini döndürüyoruz.
    #
    # Böylece modeli daha sonra JSON/UBJ olarak
    # models/ klasörüne kaydedebiliriz.
    return model


def forecast_xgb_recursive_with_change(
    series: pd.Series,
    steps: int,
    n_lags: int = 8,
) -> pd.Series:
    """
    XGBoost modelini kullanarak geleceği recursive şekilde tahmin eder.

    Parameters
    ----------
    series : pd.Series
        Modelin eğitileceği ve recursive tahminde başlangıç geçmişi
        olarak kullanılacak zaman serisi.

    steps : int
        Gelecekte tahmin edilecek hafta sayısı.

    n_lags : int, default=8
        Modelin kullanacağı geçmiş dönem sayısı.

    Returns
    -------
    pd.Series
        Gelecek haftalara ait recursive XGBoost tahminleri. Serinin
        index'i haftalık (`W-SUN`) gelecek tarihlerden oluşur.

    Notes
    -----
    Model `lag_1 ... lag_n`, `change_1` ve `change_2` feature'larını
    kullanır. Her yeni tahmin geçmiş listesine eklenir ve bir sonraki
    tahminin lag girdilerinden biri haline gelir.
    """

    # --------------------------------------------------
    # Final XGBoost modelini eğitme
    # --------------------------------------------------

    # Model training işlemini artık ayrı
    # train_xgb_model() fonksiyonuna bırakıyoruz.
    model = train_xgb_model(
        series=series,
        n_lags=n_lags,
    )

    # --------------------------------------------------
    # Feature isimlerini oluşturma
    # --------------------------------------------------

    # Eğitilen modelde kullanılan sütunların
    # sırasını burada da aynı şekilde oluşturuyoruz.
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

    # --------------------------------------------------
    # Recursive forecasting için geçmişi hazırlama
    # --------------------------------------------------

    # Tüm geçmiş değerleri float listeye çeviriyoruz.
    #
    # Recursive tahmin sırasında yeni tahminleri
    # bu listenin sonuna ekleyeceğiz.
    history = series.astype(float).tolist()

    # Gelecek tahminler burada tutulacak.
    predictions = []

    # --------------------------------------------------
    # Her gelecek hafta için tahmin üretme
    # --------------------------------------------------

    # range(steps):
    # Kaç hafta tahmin istiyorsak döngü o kadar çalışır.
    for _ in range(steps):
        # Son n_lags haftayı alıyoruz.
        #
        # İlk değer lag_1,
        # ikinci değer lag_2 ...
        lags = [
            history[-i]
            for i in range(
                1,
                n_lags + 1,
            )
        ]

        # --------------------------------------------------
        # Gelecek satırın feature'larını oluşturma
        # --------------------------------------------------

        feature_row = {f"lag_{i + 1}": lags[i] for i in range(n_lags)}

        # Son iki haftanın değişimi.
        feature_row["change_1"] = lags[0] - lags[1]

        # Ondan önceki değişim.
        feature_row["change_2"] = lags[1] - lags[2]

        # Model tek satırlık bir DataFrame bekliyor.
        X_future = pd.DataFrame(
            [feature_row],
            columns=feature_columns,
        )

        # Bir sonraki hafta için tahmin oluşturuyoruz.
        prediction = model.predict(X_future)[0]

        # Tahmini sonuç listesine ekliyoruz.
        predictions.append(prediction)

        # Recursive forecasting'in kritik kısmı:
        #
        # Tahmin edilen değeri geçmişe ekliyoruz.
        #
        # Bir sonraki döngüde bu değer artık
        # yeni lag_1 olarak kullanılacak.
        history.append(prediction)

    # --------------------------------------------------
    # Gelecek haftaların tarihlerini oluşturma
    # --------------------------------------------------

    future_index = pd.date_range(
        start=(series.index[-1] + pd.Timedelta(weeks=1)),
        periods=steps,
        freq="W-SUN",
    )

    # Tahminleri tarih index'ine sahip
    # pandas Series olarak döndürüyoruz.
    return pd.Series(
        predictions,
        index=future_index,
        name="xgb_forecast",
    )


def evaluate_ensemble_cv(
    series,
    X,
    y,
    splitter,
    n_lags=8,
    prophet_weight=0.5,
    xgb_weight=0.5,
    changepoint_prior_scale=1.0,
    yearly_seasonality="auto",
    max_depth=2,
    n_estimators=300,
    learning_rate=0.03,
    random_state=42,
    clip_range: tuple[float, float] | None = None,
):
    """
    Prophet ve XGBoost ensemble modelini time-series cross-validation ile değerlendirir.

    Parameters
    ----------
    series : pd.Series
        Değerlendirmede kullanılan tarihsel zaman serisi.

    X : pd.DataFrame
        XGBoost için hazırlanmış lag ve change feature tablosu.

    y : pd.Series
        XGBoost ve ensemble değerlendirmesinde kullanılan hedef seri.

    splitter : TimeSeriesSplit
        Zaman sırasını koruyarak train ve test fold'larını oluşturan
        scikit-learn `TimeSeriesSplit` nesnesi.

    n_lags : int, default=8
        XGBoost recursive tahmininde kullanılacak geçmiş dönem sayısı.

    prophet_weight : float, default=0.5
        Ensemble içinde Prophet tahminine verilen ağırlık.

    xgb_weight : float, default=0.5
        Ensemble içinde XGBoost tahminine verilen ağırlık.

    changepoint_prior_scale : float, default=1.0
        Prophet modelinin trend değişimlerine duyarlılığını belirler.

    yearly_seasonality : str | bool, default="auto"
        Prophet yıllık sezonsallık ayarı.

    max_depth : int, default=2
        XGBoost ağaçlarının maksimum derinliği.

    n_estimators : int, default=300
        XGBoost boosting ağacı sayısı.

    learning_rate : float, default=0.03
        XGBoost öğrenme oranı.

    random_state : int, default=42
        XGBoost eğitimindeki rastgeleliği sabitlemek için kullanılan değer.

    clip_range : tuple[float, float] | None, default=None
        Prophet, XGBoost ve ensemble tahminlerinin tutulacağı alt ve
        üst sınır. `None` ise clipping uygulanmaz.

    Returns
    -------
    pd.DataFrame
        Her cross-validation fold'u için ensemble modelinin fold numarası,
        MAE ve RMSE değerlerini içeren sonuç tablosu.

    Notes
    -----
    Her fold'da Prophet ve XGBoost yalnızca train verisi üzerinde eğitilir.
    XGBoost tahminleri recursive olarak üretilir; iki modelin tahminleri
    verilen ağırlıklarla birleştirilir.
    """

    results = []

    for fold, (train_index, test_index) in enumerate(
        splitter.split(X),
        start=1,
    ):
        # Train ve test bölümlerini al

        X_train = X.iloc[train_index]

        y_train = y.iloc[train_index]

        y_test = y.iloc[test_index]

        # -------------------------
        # Prophet
        # -------------------------

        prophet_train = pd.DataFrame(
            {
                "ds": y_train.index,
                "y": y_train.values,
            }
        )

        prophet_model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=changepoint_prior_scale,
        )

        prophet_model.fit(prophet_train)

        prophet_future = pd.DataFrame(
            {
                "ds": y_test.index,
            }
        )

        prophet_forecast = prophet_model.predict(prophet_future)

        prophet_predictions = prophet_forecast["yhat"].to_numpy()

        prophet_predictions = clip_predictions(
            prophet_predictions,
            clip_range,
        )

        # -------------------------
        # XGBoost
        # -------------------------

        xgb_model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
        )

        xgb_model.fit(
            X_train,
            y_train,
        )

        history = list(y_train.iloc[-n_lags:])

        xgb_predictions = []

        for _ in range(len(y_test)):
            lag_features = [history[-lag] for lag in range(1, n_lags + 1)]

            change_1 = lag_features[0] - lag_features[1]

            change_2 = lag_features[1] - lag_features[2]

            features = lag_features + [change_1, change_2]

            current_features = pd.DataFrame(
                [features],
                columns=X.columns,
            )

            prediction = xgb_model.predict(current_features)[0]

            if clip_range is not None:
                prediction = float(
                    np.clip(
                        prediction,
                        clip_range[0],
                        clip_range[1],
                    )
                )

            xgb_predictions.append(prediction)

            history.append(prediction)

        # -------------------------
        # Ensemble
        # -------------------------

        ensemble_predictions = (
            prophet_weight * prophet_predictions
            + xgb_weight * np.array(xgb_predictions)
        )

        ensemble_prediction = clip_predictions(
            ensemble_predictions,
            clip_range,
        )

        # -------------------------
        # Hata metrikleri
        # -------------------------

        mae = mean_absolute_error(
            y_test,
            ensemble_prediction,
        )

        rmse = root_mean_squared_error(
            y_test,
            ensemble_prediction,
        )

        results.append(
            {
                "fold": fold,
                "MAE": mae,
                "RMSE": rmse,
            }
        )

    return pd.DataFrame(results)


def select_best_model(
    model_results: dict[str, pd.DataFrame],
) -> tuple[str, pd.DataFrame]:
    """
    Ortalama MAE değeri en düşük forecasting modelini seçer.

    Parameters
    ----------
    model_results : dict[str, pd.DataFrame]
        Her forecasting modeli için cross-validation sonuçlarını içeren
        dictionary. Her sonuç tablosunda `MAE` ve `RMSE` sütunlarının
        bulunması beklenir.

    Returns
    -------
    tuple[str, pd.DataFrame]
        İlk eleman en düşük Mean MAE değerine sahip modelin adıdır.
        İkinci eleman ise modellerin Mean MAE ve Mean RMSE değerlerini
        içeren ve Mean MAE'ye göre sıralanmış karşılaştırma tablosudur.
    """

    comparison = []

    for model_name, results in model_results.items():
        comparison.append(
            {
                "Model": model_name,
                "Mean_MAE": results["MAE"].mean(),
                "Mean_RMSE": results["RMSE"].mean(),
            }
        )

    comparison_df = pd.DataFrame(comparison)

    comparison_df = comparison_df.sort_values(by="Mean_MAE").reset_index(drop=True)

    best_model = comparison_df.loc[0, "Model"]

    return best_model, comparison_df
