import pandas as pd
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose


def decompose_series(
    series: pd.Series,
    period: int = 52,
    model: str = "additive",
) -> DecomposeResult:
    """Bir zaman serisini trend, seasonal ve residual bileşenlerine ayırır."""

    decomposition = seasonal_decompose(
        series,
        model=model,
        period=period,
    )

    return decomposition


def decomposition_to_dataframe(
    decomposition: DecomposeResult,
) -> pd.DataFrame:
    """Decomposition sonucunu DataFrame'e dönüştürür."""

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
