import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.arima.model import ARIMA


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
