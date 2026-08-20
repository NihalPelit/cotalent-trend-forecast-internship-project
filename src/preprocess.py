import pandas as pd


# preprocessing fonk.
def remove_partial_rows(data: pd.DataFrame) -> pd.DataFrame:
    """
    Tamamlanmamış Google Trends satırlarını veri setinden kaldırır.

    Parameters
    ----------
    data : pd.DataFrame
        Google Trends verilerini içeren DataFrame.
        DataFrame içerisinde `isPartial` sütununun bulunması beklenir.

    Returns
    -------
    pd.DataFrame
        `isPartial=False` olan, yani tamamlanmış dönemleri içeren
        bağımsız bir DataFrame kopyası.

    Notes
    -----
    Google Trends verilerinde `isPartial=True`, ilgili zaman döneminin
    henüz tamamlanmadığını belirtir. Bu satırlar analiz ve forecasting
    sırasında yanıltıcı olabileceği için veri setinden çıkarılır.

    `~data["isPartial"]` ifadesindeki `~` operatörü Boolean değerleri
    tersine çevirir. Böylece `isPartial=False` olan tamamlanmış satırlar
    seçim maskesinde `True` hale gelir.

    `.copy()` kullanılması, temizlenen verinin orijinal DataFrame'den
    bağımsız bir kopya olarak oluşturulmasını sağlar.
    """

    clean_data = data[
        ~data["isPartial"]
    ].copy()  # boolean series içindekileri tek tek tersine çeviriyor, data[mask] yaptığında sadece mask değeri True olan satırlar alınır.

    return clean_data
