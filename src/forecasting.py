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


def forecast_prophet(
    series: pd.Series,
    steps: int,
    changepoint_prior_scale: float = 1.0,
    yearly_seasonality="auto",
) -> pd.DataFrame:
    """Prophet modelini tüm seri üzerinde eğitir ve ileri tahmin üretir."""

    data = series.rename("y").reset_index().rename(columns={"date": "ds"})

    model = Prophet(
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=changepoint_prior_scale,
    )

    model.fit(data)

    future = model.make_future_dataframe(
        periods=steps,
        freq="W-SUN",
    )

    forecast = model.predict(future)

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


def forecast_xgb_recursive_with_change(
    series: pd.Series,
    steps: int,
    n_lags: int = 8,
) -> pd.Series:
    """
    Forecast future values recursively using XGBoost.

    The model uses:
    - lag_1 ... lag_8
    - change_1
    - change_2

    Parameters
    ----------
    series : pd.Series
        Historical time series.

    steps : int
        Number of future periods to forecast.

    n_lags : int, default=8
        Number of lag features.

    Returns
    -------
    pd.Series
        Recursive future forecasts.
    """

    # --------------------------------------------------
    # Training data
    # --------------------------------------------------

    lag_data = pd.DataFrame(
        {
            "target": series,
            **{f"lag_{i}": series.shift(i) for i in range(1, n_lags + 1)},
        }
    ).dropna()

    # Change features

    lag_data["change_1"] = lag_data["lag_1"] - lag_data["lag_2"]

    lag_data["change_2"] = lag_data["lag_2"] - lag_data["lag_3"]

    feature_columns = [
        *[f"lag_{i}" for i in range(1, n_lags + 1)],
        "change_1",
        "change_2",
    ]

    X = lag_data[feature_columns]
    y = lag_data["target"]

    # --------------------------------------------------
    # Final XGBoost model
    # --------------------------------------------------

    model = XGBRegressor(
        n_estimators=300,
        max_depth=2,
        learning_rate=0.03,
        random_state=42,
    )

    model.fit(X, y)

    # --------------------------------------------------
    # Recursive forecasting
    # --------------------------------------------------

    history = series.astype(float).tolist()

    predictions = []

    for _ in range(steps):
        lags = [history[-i] for i in range(1, n_lags + 1)]

        feature_row = {f"lag_{i + 1}": lags[i] for i in range(n_lags)}

        feature_row["change_1"] = lags[0] - lags[1]

        feature_row["change_2"] = lags[1] - lags[2]

        X_future = pd.DataFrame(
            [feature_row],
            columns=feature_columns,
        )

        prediction = model.predict(X_future)[0]

        predictions.append(prediction)

        # Tahmin edilen değer geçmişe ekleniyor.
        # Bir sonraki haftanın lag_1 değeri artık bu tahmin olacak.
        history.append(prediction)

    # --------------------------------------------------
    # Future dates
    # --------------------------------------------------

    future_index = pd.date_range(
        start=series.index[-1] + pd.Timedelta(weeks=1),
        periods=steps,
        freq="W-SUN",
    )

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
