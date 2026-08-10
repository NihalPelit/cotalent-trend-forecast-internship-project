import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor


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


def evaluate_arima_cv(
    series: pd.Series,
    splitter: TimeSeriesSplit,
    order: tuple[int, int, int],
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
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=changepoint_prior_scale,
        )

        model.fit(train_df)

        forecast = model.predict(test_df[["ds"]])

        mae = mean_absolute_error(
            test_df["y"],
            forecast["yhat"],
        )

        rmse = root_mean_squared_error(
            test_df["y"],
            forecast["yhat"],
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
) -> pd.DataFrame:
    """Prophet modelini tüm seri üzerinde eğitir ve ileri tahmin üretir."""

    data = series.rename("y").reset_index().rename(columns={"date": "ds"})

    model = Prophet(
        yearly_seasonality=True,
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
