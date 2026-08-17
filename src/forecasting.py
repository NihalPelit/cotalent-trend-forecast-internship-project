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
    Tahminleri belirtilen alt ve üst sınırlar arasında tutar.

    Örneğin Google Trends için:
    clip_range=(0, 100)
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
    """Naive modeli time-series cross-validation ile değerlendirir."""

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
    Son gözlenen değeri gelecek dönemler için
    tahmin olarak kullanır.
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
    """ARIMA modelini time-series cross-validation ile değerlendirir."""

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
    """ARIMA modelini tüm seri üzerinde eğitir ve ileri tahmin üretir."""

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
    """Prophet modelini time-series cross-validation ile değerlendirir."""

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
        Eğitilecek zaman serisi.

    changepoint_prior_scale : float, default=1.0
        Prophet modelinin trend değişimlerine ne kadar
        esnek tepki vereceğini belirler.

    yearly_seasonality : str | bool, default="auto"
        Yıllık sezonsallığın kullanılıp kullanılmayacağını belirler.

    Returns
    -------
    Prophet
        Eğitilmiş Prophet model nesnesi.
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
    Prophet modelini tüm seri üzerinde eğitir
    ve ileriye yönelik tahmin üretir.
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
    """XGBoost modelini recursive time-series CV ile değerlendirir."""

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
    Lag ve change feature'larını kullanarak
    XGBoost modelini tüm seri üzerinde eğitir.

    Parameters
    ----------
    series : pd.Series
        Eğitilecek zaman serisi.

    n_lags : int, default=8
        Modelin kullanacağı geçmiş hafta sayısı.

    max_depth : int, default=2
        XGBoost ağaçlarının maksimum derinliği.

    n_estimators : int, default=300
        Kullanılacak toplam boosting ağacı sayısı.

    learning_rate : float, default=0.03
        Her ağacın modele katkısının büyüklüğü.

    random_state : int, default=42
        Sonuçların tekrar üretilebilir olmasını sağlar.

    Returns
    -------
    XGBRegressor
        Eğitilmiş XGBoost model nesnesi.
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
    Eğitilmiş XGBoost mantığını kullanarak
    geleceği recursive şekilde tahmin eder.

    Model feature'ları:

    - lag_1 ... lag_n
    - change_1
    - change_2
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
    Evaluate a Prophet + XGBoost ensemble using
    time-series cross-validation.
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
    Select the forecasting model with the lowest mean MAE.

    Parameters
    ----------
    model_results : dict[str, pd.DataFrame]
        Dictionary containing cross-validation results
        for each forecasting model.

    Returns
    -------
    tuple[str, pd.DataFrame]
        Name of the best model and a comparison table
        sorted by mean MAE.
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
