import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Dashboard Wisata Indonesia",
    page_icon=":palm_tree:",
    layout="wide"
)
st.title(":palm_tree: Dashboard Wisata Indonesia")
st.write(
    "Dashboard interaktif untuk melihat persebaran dan karakteristik "
    "destinasi wisata di Indonesia."
)
st.divider()

DATA_FILE = "wisata_indonesia_new.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)
    data["latitude"] = pd.to_numeric(
        data["latitude"], errors="coerce"
    )
    data["longitude"] = pd.to_numeric(
        data["longitude"], errors="coerce"
    )
    return data
data = load_data()

data.columns = data.columns.str.strip()
kolom_teks = [
    "kategori",
    "nama_wisata",
    "alamat",
    "provinsi",
    "kota_kabupaten"
]

for kolom in kolom_teks:
    if kolom in data.columns:
        data[kolom] = data[kolom].fillna("Tidak diketahui")

st.sidebar.header(":mag_right: Filter Data")

# Filter provinsi
provinsi_list = sorted(
    data["provinsi"].dropna().unique().tolist()
)

pilih_provinsi = st.sidebar.multiselect(
    "Pilih Provinsi",
    options=provinsi_list,
    default=[]
)

# Filter kategori
kategori_list = sorted(
    data["kategori"].dropna().unique().tolist()
)

pilih_kategori = st.sidebar.multiselect(
    "Pilih Kategori Wisata",
    options=kategori_list,
    default=[]
)

# MENERAPKAN FILTER
filtered_data = data.copy()
if pilih_provinsi:
    filtered_data = filtered_data[
        filtered_data["provinsi"].isin(pilih_provinsi)
    ]
if pilih_kategori:
    filtered_data = filtered_data[
        filtered_data["kategori"].isin(pilih_kategori)
    ]

# Menghitung rata-rata jumlah destinasi per provinsi
jumlah_destinasi_provinsi = filtered_data["provinsi"].value_counts()
rata_rata_destinasi = np.mean(jumlah_destinasi_provinsi)

# INFORMASI DATA
st.subheader(":bar_chart: Ringkasan Data")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        "Total Destinasi",
        len(filtered_data)
    )
with col2:
    st.metric(
        "Jumlah Provinsi",
        filtered_data["provinsi"].nunique()
    )
with col3:
    st.metric(
        "Kategori Wisata",
        filtered_data["kategori"].nunique()
    )
with col4:
    st.metric(
        "Kota/Kabupaten",
        filtered_data["kota_kabupaten"].nunique()
    )
with col5:
    st.metric(
        "Rata-rata Destinasi/Provinsi",
        f"{rata_rata_destinasi:.2f}"
    )
st.divider()

# GRAFIK KATEGORI WISATA
st.subheader(":chart_with_upwards_trend: Jumlah Destinasi Berdasarkan Kategori")
kategori_count = (
    filtered_data["kategori"]
    .value_counts()
    .sort_values(ascending=False)
)
st.bar_chart(kategori_count)

# GRAFIK PROVINSI
st.subheader(":earth_asia: Jumlah Destinasi Berdasarkan Provinsi")
provinsi_count = (
    filtered_data["provinsi"]
    .value_counts()
    .sort_values(ascending=False)
)
st.bar_chart(provinsi_count)

# PETA PERSEBARAN WISATA
st.subheader(":round_pushpin: Persebaran Destinasi Wisata")
map_data = filtered_data[
    ["latitude", "longitude"]
].dropna()

map_data = map_data.rename(
    columns={
        "latitude": "lat",
        "longitude": "lon"
    }
)

if len(map_data) > 0:
    st.map(map_data)
else:
    st.warning(
        "Tidak terdapat data koordinat untuk ditampilkan pada peta."
    )
st.divider()

# DATA DESTINASI WISATA
st.subheader(":palm_tree: Daftar Destinasi Wisata")
tabel_data = filtered_data[
    [
        "nama_wisata",
        "kategori",
        "provinsi",
        "kota_kabupaten",
        "alamat"
    ]
].copy()

tabel_data.columns = [
    "Nama Wisata",
    "Kategori",
    "Provinsi",
    "Kota/Kabupaten",
    "Alamat"
]

st.dataframe(
    tabel_data,
    use_container_width=True,
    hide_index=True
)

# DETAIL DESTINASI
st.divider()
st.subheader(":mag_right: Detail Destinasi")

if len(filtered_data) > 0:

    pilihan_wisata = st.selectbox(
        "Pilih destinasi wisata:",
        filtered_data["nama_wisata"].tolist()
    )
    detail = filtered_data[
        filtered_data["nama_wisata"] == pilihan_wisata
    ].iloc[0]
    col1, col2 = st.columns([1, 2])

    # GAMBAR
    with col1:
        gambar = None

        # Prioritas menggunakan Image_Path
        if "Image_Path" in detail.index:
            if pd.notna(detail["Image_Path"]):
                gambar = detail["Image_Path"]
        # Jika tidak ada, coba path_gambar
        if not gambar and "path_gambar" in detail.index:
            if pd.notna(detail["path_gambar"]):
                gambar = detail["path_gambar"]
        if gambar:
            try:
                st.image(
                    gambar,
                    caption=detail["nama_wisata"],
                    use_container_width=True
                )
            except Exception:
                st.info("Gambar tidak dapat ditampilkan.")
        else:
            st.info("Gambar tidak tersedia.")

    # INFORMASI DESTINASI
    with col2:
        st.markdown(
            f"### {detail['nama_wisata']}"
        )
        st.write(
            f"**Kategori:** {detail['kategori']}"
        )
        st.write(
            f"**Provinsi:** {detail['provinsi']}"
        )
        st.write(
            f"**Kota/Kabupaten:** {detail['kota_kabupaten']}"
        )
        st.write(
            f"**Alamat:** {detail['alamat']}"
        )

        if "deskripsi_bersih" in detail.index:
            if pd.notna(detail["deskripsi_bersih"]):
                st.write("**Deskripsi:**")
                st.write(
                    detail["deskripsi_bersih"]
                )
        st.write(
            f"**Latitude:** {detail['latitude']}"
        )
        st.write(
            f"**Longitude:** {detail['longitude']}" 
        )
st.divider()