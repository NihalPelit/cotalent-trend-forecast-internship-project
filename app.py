# --------------------------------------------------
# Trend Forecast Dashboard
# --------------------------------------------------

# Path:
# Projedeki data/, models/ gibi klasörlere
# güvenli dosya yolları oluşturmak için kullanıyoruz.
from pathlib import Path

# Pandas:
# CSV verisini okumak ve zaman serileriyle
# çalışmak için kullanıyoruz.
import pandas as pd

# Plotly:
# İnteraktif zaman serisi grafikleri
# oluşturmak için kullanacağız.
import plotly.graph_objects as go

# Streamlit:
# Python kodumuzu web tabanlı bir dashboard'a
# dönüştüren kütüphane.
import streamlit as st

# Kendi oluşturduğumuz pipeline.py içinden:
#
# generate_final_forecast:
# Kaydedilmiş modelleri kullanarak
# 4 haftalık final forecast üretir.
#
# load_model_metadata:
# Final modeller hakkındaki metadata
# bilgilerini JSON dosyasından okur.
from src.pipeline import (
    generate_final_forecast,
    load_model_metadata,
)

# detect_anomalies:
# Seçilen trendin son gözleminin
# geçmiş davranışına göre sıra dışı olup
# olmadığını kontrol eder.
from src.monitoring import (
    detect_anomalies,
    detect_rising_trend_signal,
)


# --------------------------------------------------
# Sayfa ayarları
# --------------------------------------------------

# Streamlit'te set_page_config() mümkün olduğunca
# ilk Streamlit komutu olmalıdır.
st.set_page_config(
    page_title="Trend Forecast Dashboard",
    page_icon="📈",
    layout="wide",
)


# --------------------------------------------------
# Proje yollarını belirleme
# --------------------------------------------------

# __file__:
# Şu anda çalışan Python dosyasının yoludur.
#
# Burada çalışan dosya:
# app.py
#
# resolve():
# Dosyanın tam yolunu elde eder.
#
# parent:
# app.py'nin bulunduğu klasörü verir.
#
# app.py proje ana klasöründe olduğu için
# project_root doğrudan proje klasörümüz olur.
project_root = Path(__file__).resolve().parent


# Güncel Google Trends verisinin yolu.
data_path = (
    project_root / "data" / "processed" / "google_trends_ai_3y_updated_2026-08-09.csv"
)


# Kaydedilmiş modellerin bulunduğu klasör.
models_dir = project_root / "models"


# Final model konfigürasyonunu açıklayan
# metadata JSON dosyasının yolu.
metadata_path = models_dir / "model_metadata_as_of_2026-08-09.json"


# --------------------------------------------------
# Dashboard başlığı
# --------------------------------------------------

st.title("📈 Trend Forecast Dashboard")

st.write(
    "Google Trends verileri kullanılarak "
    "AI teknolojilerinin geçmiş eğilimlerini "
    "ve gelecek 4 haftalık tahminlerini inceleyebilirsiniz."
)


# --------------------------------------------------
# Veriyi ve final forecast'u yükleme
# --------------------------------------------------

# try-except:
#
# Dashboard çalışırken dosya bulunamaması,
# veri okunamaması veya model yükleme problemi
# oluşursa uygulamanın tamamen çökmesi yerine
# kullanıcıya anlaşılır bir hata göstermek istiyoruz.
try:
    # --------------------------------------------------
    # Güncel veri
    # --------------------------------------------------

    # parse_dates=["date"]:
    # date sütununu normal string yerine
    # datetime olarak okur.
    #
    # index_col="date":
    # tarihi DataFrame index'i yapar.
    updated_data = pd.read_csv(
        data_path,
        parse_dates=["date"],
        index_col="date",
    )

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    # Model seçimleri ve parametre bilgileri
    # metadata JSON dosyasından geliyor.
    metadata = load_model_metadata(metadata_path)

    # --------------------------------------------------
    # Final forecast
    # --------------------------------------------------

    # Burada modeller YENİDEN eğitilmiyor.
    #
    # pipeline.py:
    #
    # models/ içindeki Prophet ve XGBoost
    # modellerini yükler,
    #
    # Gemini ve Claude için Naive forecast üretir,
    #
    # sonra üç trendin final forecast'unu
    # tek DataFrame olarak döndürür.
    final_forecast = generate_final_forecast(
        data=updated_data,
        models_dir=models_dir,
        metadata_path=metadata_path,
    )


except Exception as error:
    # Kullanıcıya dashboard üzerinde hata mesajı gösterir.
    st.error(f"Veriler veya modeller yüklenirken hata oluştu: {error}")

    # st.stop():
    # Bu noktadan sonraki Streamlit kodunun
    # çalışmasını durdurur.
    #
    # Çünkü veri/model yüklenememişse aşağıdaki
    # grafiklerin çalışması mümkün değildir.
    st.stop()


# --------------------------------------------------
# Trend seçimi
# --------------------------------------------------

st.subheader("Trend Seçimi")


# st.selectbox():
# Kullanıcıya açılır seçim kutusu gösterir.
#
# Dönen değer kullanıcının seçtiği metindir.
selected_trend = st.selectbox(
    "İncelemek istediğiniz teknolojiyi seçin:",
    [
        "ChatGPT",
        "Gemini",
        "Claude",
    ],
)


# --------------------------------------------------
# Dashboard adı ile veri sütunu arasındaki eşleştirme
# --------------------------------------------------

# CSV içerisindeki sütunlarımız küçük harfle:
#
# chatgpt
# gemini
# claude
#
# Ancak kullanıcıya daha güzel görünen isimleri:
#
# ChatGPT
# Gemini
# Claude
#
# gösteriyoruz.
#
# Bu dictionary iki yapı arasında bağlantı kuruyor.
column_map = {
    "ChatGPT": "chatgpt",
    "Gemini": "gemini",
    "Claude": "claude",
}


# Kullanıcının seçimine karşılık gelen
# gerçek DataFrame sütununu buluyoruz.
selected_column = column_map[selected_trend]


# --------------------------------------------------
# Seçilen trendin geçmiş verisi
# --------------------------------------------------

historical_series = updated_data[selected_column]

# --------------------------------------------------
# Anomaly monitoring
# --------------------------------------------------

# Seçilen trendin tüm geçmişi üzerinde
# anomaly detection çalıştırıyoruz.
anomaly_results = detect_anomalies(
    series=historical_series,
    # Day 10 analizinde seçtiğimiz
    # final/provisional monitoring parametreleri.
    window=12,
    threshold=3.5,
    min_absolute_change=5.0,
)


# Son haftanın anomaly bilgilerini alıyoruz.
latest_anomaly = anomaly_results.iloc[-1]


# Son haftanın anomaly score'u.
latest_anomaly_score = latest_anomaly["Anomaly_Score"]


# Son gözlem anomaly mi?
latest_is_anomaly = bool(latest_anomaly["Is_Anomaly"])


# --------------------------------------------------
# Seçilen trendin gelecek tahmini
# --------------------------------------------------

# final_forecast DataFrame'inde sütun isimleri
# zaten kullanıcıya gösterdiğimiz formatta:
#
# ChatGPT
# Gemini
# Claude
forecast_series = final_forecast[selected_trend]

# --------------------------------------------------
# Gelecek trend sinyali
# --------------------------------------------------

# Son gerçek Google Trends değerini alıyoruz.
current_value = float(historical_series.iloc[-1])


# Final forecast'un gelecekte belirgin ve
# devamlı bir yükseliş gösterip göstermediğini
# kontrol ediyoruz.
trend_signal = detect_rising_trend_signal(
    current_value=current_value,
    forecast=forecast_series,
    min_total_increase=5.0,
    min_positive_ratio=0.75,
)


# --------------------------------------------------
# Kullanılan final modeli belirleme
# --------------------------------------------------

# Metadata'da trend anahtarları küçük harfle
# tutulduğu için selected_column'u kullanıyoruz.
selected_model = metadata[selected_column]["selected_model"]


# Kullanıcıya daha anlaşılır model adı gösteriyoruz.
if selected_model == "ensemble":
    selected_model_display = "Prophet + XGBoost Ensemble"

else:
    selected_model_display = selected_model.capitalize()


# --------------------------------------------------
# Özet değerler
# --------------------------------------------------

# Son gerçek Google Trends değeri.
last_value = float(historical_series.iloc[-1])


# Forecast'un son haftasındaki tahmin.
forecast_end_value = float(forecast_series.iloc[-1])


# Bugünkü değer ile 4 hafta sonraki forecast
# arasındaki puan farkı.
forecast_change = forecast_end_value - last_value


# --------------------------------------------------
# Bilgi kartları
# --------------------------------------------------

# st.columns(3):
# Ekranı yatay olarak üç bölüme ayırır.
metric_col_1, metric_col_2, metric_col_3 = st.columns(3)


# Birinci kart:
# Son gerçek Google Trends değeri.
with metric_col_1:
    st.metric(
        label="Son Gözlenen Skor",
        value=f"{last_value:.1f}",
    )


# İkinci kart:
# Dördüncü haftanın forecast değeri.
with metric_col_2:
    st.metric(
        label="4 Hafta Sonrası Tahmin",
        value=f"{forecast_end_value:.1f}",
        # delta:
        # mevcut değer ile gelecek değer arasındaki
        # değişimi küçük ek bilgi olarak gösterir.
        delta=f"{forecast_change:+.1f} puan",
    )


# Üçüncü kart:
# Bu trend için seçilmiş final model.
with metric_col_3:
    st.metric(
        label="Final Model",
        value=selected_model_display,
    )

# --------------------------------------------------
# Güncel monitoring durumu
# --------------------------------------------------

st.subheader("Güncel Trend Monitoring")


# Eğer son gözlem anomaly ise
# kullanıcıya uyarı gösteriyoruz.
if latest_is_anomaly:
    st.warning(
        f"⚠️ {selected_trend} için son gözlem "
        "yakın geçmişe göre sıra dışı bir hareket gösteriyor. "
        f"Anomaly Score: {latest_anomaly_score:.2f}"
    )


# Anomaly değilse normal bilgi mesajı gösteriyoruz.
else:
    st.success(
        f"✅ {selected_trend} için son gözlemde "
        "güçlü bir anomaly tespit edilmedi. "
        f"Anomaly Score: {latest_anomaly_score:.2f}"
    )

# --------------------------------------------------
# Gelecek trend early-warning
# --------------------------------------------------

st.subheader("Gelecek Trend Sinyali")

if trend_signal["is_rising_signal"]:
    st.warning(
        f"📈 Yükselen Trend Sinyali! "
        f"{selected_trend} için önümüzdeki "
        f"4 haftada yaklaşık "
        f"{trend_signal['total_increase']:+.1f} puanlık "
        "bir yükseliş öngörülüyor."
    )

else:
    st.info(
        f"ℹ️ {selected_trend} için şu anda "
        "güçlü bir yükselen trend sinyali bulunmuyor. "
        f"4 haftalık beklenen değişim: "
        f"{trend_signal['total_increase']:+.1f} puan."
    )

# --------------------------------------------------
# İnteraktif zaman serisi grafiği
# --------------------------------------------------

st.subheader(f"{selected_trend} — Geçmiş ve Gelecek Trend")


# Plotly grafik nesnesi oluşturuyoruz.
figure = go.Figure()


# --------------------------------------------------
# Gerçek geçmiş veri
# --------------------------------------------------

figure.add_trace(
    go.Scatter(
        # X ekseni:
        # tarihler
        x=historical_series.index,
        # Y ekseni:
        # Google Trends skorları
        y=historical_series.values,
        # Çizgi grafik
        mode="lines",
        # Grafikteki seri adı
        name="Gerçek Veri",
        # Mouse değer üzerine geldiğinde
        # gösterilecek bilgi.
        hovertemplate=("Tarih: %{x|%Y-%m-%d}<br>Trend Skoru: %{y:.1f}<extra></extra>"),
    )
)

# --------------------------------------------------
# Geçmiş anomaly noktaları
# --------------------------------------------------

# anomaly_results içerisinde yalnızca
# Is_Anomaly = True olan satırları seçiyoruz.
#
# Bu DataFrame artık sadece geçmişte sistemin
# sıra dışı olarak değerlendirdiği tarihleri içerir.
historical_anomalies = anomaly_results[anomaly_results["Is_Anomaly"]]


# .empty:
# DataFrame'in boş olup olmadığını kontrol eder.
#
# historical_anomalies.empty = True
# → hiç anomaly yok
#
# not historical_anomalies.empty
# → en az bir anomaly var
if not historical_anomalies.empty:
    # Anomaly noktalarını gerçek trend çizgisinin
    # üzerine ayrı bir trace olarak ekliyoruz.
    figure.add_trace(
        go.Scatter(
            # X ekseni:
            # anomaly görülen tarihler
            x=historical_anomalies.index,
            # Y ekseni:
            # anomaly tarihlerindeki gerçek trend skorları
            y=historical_anomalies["Value"],
            # Sadece noktalar gösterilsin.
            # Aralarında çizgi istemiyoruz.
            mode="markers",
            # Legend'da görünen isim.
            name="Anomaly",
            # Noktaları normal trend çizgisinden
            # ayırmak için X sembolü kullanıyoruz.
            marker={
                "size": 11,
                "symbol": "x",
            },
            # customdata:
            # Her anomaly noktasına anomaly score bilgisini
            # ek olarak bağlıyoruz.
            #
            # Bu bilgi grafikte doğrudan görünmez;
            # hovertemplate içinde kullanacağız.
            customdata=historical_anomalies["Anomaly_Score"],
            # Mouse anomaly noktasının üzerine geldiğinde
            # gösterilecek bilgiler.
            hovertemplate=(
                "Tarih: %{x|%Y-%m-%d}<br>"
                "Trend Skoru: %{y:.1f}<br>"
                "Anomaly Score: %{customdata:.2f}"
                "<extra></extra>"
            ),
        )
    )


# --------------------------------------------------
# Forecast çizgisini gerçek veriye bağlama
# --------------------------------------------------

# Eğer forecast sadece gelecekteki tarihlerden
# başlarsa gerçek veri ile arasında küçük bir
# görsel boşluk oluşabilir.
#
# Bu nedenle son gerçek gözlemi forecast serisinin
# başına ekliyoruz.
forecast_with_connection = pd.concat(
    [
        historical_series.tail(1),
        forecast_series,
    ]
)


# --------------------------------------------------
# Forecast çizgisi
# --------------------------------------------------

figure.add_trace(
    go.Scatter(
        x=forecast_with_connection.index,
        y=forecast_with_connection.values,
        mode="lines+markers",
        name="Final Forecast",
        # dash="dash":
        # Forecast bölümünü kesikli çizgi yaparak
        # gerçek veriden görsel olarak ayırıyoruz.
        line={"dash": "dash"},
        hovertemplate=("Tarih: %{x|%Y-%m-%d}<br>Tahmin: %{y:.1f}<extra></extra>"),
    )
)


# --------------------------------------------------
# Grafik görünüm ayarları
# --------------------------------------------------

figure.update_layout(
    title=(f"{selected_trend} Google Trends Geçmiş Verisi ve 4 Haftalık Forecast"),
    xaxis_title="Tarih",
    yaxis_title="Google Trends Skoru",
    # Mouse'u grafiğin üzerine getirince
    # x eksenindeki serileri birlikte gösterir.
    hovermode="x unified",
    # Dashboard genişliğine uygun yükseklik.
    height=550,
)


# Google Trends skorları doğal olarak
# 0 ile 100 arasındadır.
figure.update_yaxes(
    range=[
        0,
        100,
    ]
)


# Plotly grafiğini Streamlit üzerinde gösteriyoruz.
#
# use_container_width=True:
# Grafik bulunduğu ekran alanını doldurur.
st.plotly_chart(
    figure,
    use_container_width=True,
)


# --------------------------------------------------
# Forecast tablosu
# --------------------------------------------------

st.subheader("4 Haftalık Tahmin")


# Forecast Series'i daha okunabilir
# bir DataFrame haline getiriyoruz.
forecast_table = forecast_series.rename("Tahmin").to_frame()


# Index ismini kullanıcıya uygun hale getiriyoruz.
forecast_table.index.name = "Tarih"


# Sayısal değerleri iki ondalık basamakla gösteriyoruz.
st.dataframe(
    forecast_table.style.format({"Tahmin": "{:.2f}"}),
    use_container_width=True,
)
