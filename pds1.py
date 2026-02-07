import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

st.title("Dashboard GIS Persebaran Sekolah")
st.write("Visualisasi persebaran sekolah dengan GIS ")

df = pd.read_excel("data_sekolah_Final.xlsx")

def klasifikasi_jenjang(nama):
    if pd.isna(nama):
        return "LAINNYA"

    nama = str(nama).upper().strip()

    sd_prefix = ["SD", "SDN", "SDS", "SDIT", "MIS", "SDI", "MI"]
    smp_prefix = ["SMP", "SMPN", "SMPS", "MTSS", "MTS", "SMPIT"]

    kata_pertama = nama.split()[0]

    if kata_pertama in sd_prefix:
        return "SD"
    elif kata_pertama in smp_prefix:
        return "SMP"
    else:
        return "LAINNYA"

df["Jenjang"] = df["Nama Sekolah"].apply(klasifikasi_jenjang)

st.sidebar.header("Filter Jenjang")

jenjang_filter = st.sidebar.multiselect(
    "Pilih Jenjang",
    options=sorted(df["Jenjang"].unique()),
    default=sorted(df["Jenjang"].unique())
)

st.sidebar.header("Filter Status")

status_filter = st.sidebar.multiselect(
    "Pilih Status Sekolah",
     options=sorted(df["Status"].dropna().unique()),
    default=sorted(df["Status"].dropna().unique())
)

st.sidebar.header("Filter Kecamatan")
kec_filter = st.sidebar.multiselect(
    "Pilih Daftar KeLurahan atau Desa",
    options=sorted(df["Kelurahan/Desa"].dropna().unique()),
    default=sorted(df["Kelurahan/Desa"].dropna().unique())
)

if not jenjang_filter:
    jenjang_filter = df["Jenjang"].unique().tolist()

if not status_filter:
    status_filter = df["Status"].dropna().unique().tolist()

if not kec_filter:
    kec_filter = df["Kelurahan/Desa"].dropna().unique().tolist()

df_filter = df[
    (df["Jenjang"].isin(jenjang_filter)) &
    (df["Status"].isin(status_filter)) &
    (df["Kelurahan/Desa"].isin(kec_filter))
]

col1, col2, col3 = st.columns(3)
col1.metric("Total Sekolah", len(df_filter))
col2.metric("Sekolah Negeri", (df_filter["Status"] == "NEGERI").sum())
col3.metric("Sekolah Swasta", (df_filter["Status"] == "SWASTA").sum())

st.subheader("Peta Persebaran Sekolah (GIS)")

m = folium.Map(location=[-6.5626, 106.6289], zoom_start=10)
jumlah_titik = 0

for _, row in df_filter.iterrows():
    try:
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])

        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            popup=f"""
            <b>Nama Sekolah:</b> {row['Nama Sekolah']}<br>
            <b>Status:</b> {row['Status']}<br>
            <b>Kelurahan:</b> {row['Kelurahan/Desa']}<br>
            <b>Kode Kecamatan:</b> {row['Kode Kecamatan']}
            """,
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

        jumlah_titik += 1
    except:
        pass

st_folium(m, width=1200, height=600)
st.info(f"Jumlah titik sekolah yang berhasil ditampilkan: {jumlah_titik}")

st.subheader("Perbandingan Sekolah Swasta dan Negeri")

if df_filter.empty:
    st.warning("Data kosong untuk filter yang dipilih.")
else:
    fig_status, ax_status = plt.subplots()
    df_filter["Status"].value_counts().plot(kind="bar", ax=ax_status)
    ax_status.set_xlabel("Status")
    ax_status.set_ylabel("Jumlah Sekolah")
    ax_status.set_title("Perbandingan Sekolah Swasta dan Negeri")
    st.pyplot(fig_status)

st.subheader("Perbandingan Jumlah Sekolah SD dan SMP")

if df_filter.empty:
    st.warning("Data kosong untuk filter yang dipilih.")
else:
    fig_jenjang, ax_jenjang = plt.subplots()

    df_filter["Jenjang"].value_counts().reindex(["SD", "SMP"], fill_value=0).plot(
        kind="bar",
        ax=ax_jenjang
    )

    ax_jenjang.set_xlabel("Jenjang")
    ax_jenjang.set_ylabel("Jumlah Sekolah")
    ax_jenjang.set_title("Perbandingan Jumlah Sekolah SD dan SMP")

    st.pyplot(fig_jenjang)

st.subheader("Top 10 Kecamatan dengan sekolah terbanyak")
if df_filter.empty:
    st.warning("Data kosong untuk filter yang dipilih.")
else:
    fig_kec, ax_kec = plt.subplots()
    df_filter["Kelurahan/Desa"].value_counts().head(10).plot(
        kind="bar",
        ax=ax_kec
    )

    ax_kec.set_xlabel("Nama Kecamatan")
    ax_kec.set_ylabel("Jumlah Sekolah")
    ax_kec.set_title("Top 10 Kecamatan dengan Sekolah Terbanyak")
    st.pyplot(fig_kec)

st.subheader("📄 Data Sekolah ")
st.dataframe(df_filter)
