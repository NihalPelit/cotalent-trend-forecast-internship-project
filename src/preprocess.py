import pandas as pd

# preprocessing fonk.
def remove_partial_rows(data: pd.DataFrame) -> pd.DataFrame:
    """Tamamlanmamış Google Trends satırlarını kaldırır."""

    clean_data = data[~data["isPartial"]].copy() # boolean series içindekileri tek tek tersine çeviriyor, data[mask]] yaptığında sadece mask değeri True olan satırlar alınır.

    return clean_data