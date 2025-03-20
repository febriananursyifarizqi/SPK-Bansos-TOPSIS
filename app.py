import streamlit as st
import pandas as pd
import numpy as np
import os

# Fungsi Normalisasi TOPSIS
def normalize_topsis(df):
    X = df.iloc[:, 1:].copy().astype(float)
    X_norm = X / np.sqrt((X ** 2).sum(axis=0))
    return X_norm

# Fungsi Perhitungan TOPSIS
def calculate_topsis(df):
    X_norm = normalize_topsis(df)
    X_weighted = X_norm * list(weights.values())
    
    # Menentukan solusi ideal positif (A+) dan negatif (A-)
    A_plus = np.array([
        max(X_weighted[col]) if criteria_types[col] == "benefit" else min(X_weighted[col])
        for col in df.columns[1:]
    ])
    A_minus = np.array([
        min(X_weighted[col]) if criteria_types[col] == "benefit" else max(X_weighted[col])
        for col in df.columns[1:]
    ])
    
    # Menghitung jarak solusi positif dan negatif
    D_plus = np.sqrt(((X_weighted - A_plus) ** 2).sum(axis=1))
    D_minus = np.sqrt(((X_weighted - A_minus) ** 2).sum(axis=1))
    
    # Menghitung skor preferensi
    C = D_minus / (D_plus + D_minus)
    return C

st.title("Sistem Pendukung Keputusan Penentuan Warga Penerima Bantuan Sosial 📦")

# Load dataset dengan error handling
script_dir = os.path.dirname(os.path.realpath(__file__))
file_path = f"{script_dir}/datapenduduk.csv"
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    st.error("File data tidak ditemukan!")
    st.stop()

# Menampilkan data penduduk
st.subheader("Data Penduduk")
st.dataframe(df)

criteria_types = {
    "Usia (C1)": "benefit",
    "Pendidikan (C2)": "cost",
    "Pekerjaan (C3)": "cost",
    "Penghasilan (C4)": "cost",
    "Tanggungan (C5)": "benefit",
    "Tempat Tinggal (C6)": "cost",
    "Keluarga Sakit (C7)": "benefit",
    "Keluarga Lansia (C8)": "benefit",
}

# Sidebar untuk memasukkan bobot
with st.sidebar:
    st.image(f"{script_dir}/bansos.png")
    st.subheader("Masukkan Bobot Kriteria")
    weights = {}
    
    with st.form("Preferensi"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            weights["Usia (C1)"] = st.number_input("C1", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
            weights["Tanggungan (C5)"] = st.number_input("C5", min_value=0.0, max_value=1.0, value=0.20, step=0.01)

        with col2:
            weights["Pendidikan (C2)"] = st.number_input("C2", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
            weights["Tempat Tinggal (C6)"] = st.number_input("C6", min_value=0.0, max_value=1.0, value=0.10, step=0.01)

        with col3:
            weights["Pekerjaan (C3)"] = st.number_input("C3", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
            weights["Keluarga Sakit (C7)"] = st.number_input("C7", min_value=0.0, max_value=1.0, value=0.08, step=0.01)

        with col4:
            weights["Penghasilan (C4)"] = st.number_input("C4", min_value=0.0, max_value=1.0, value=0.25, step=0.01)
            weights["Keluarga Lansia (C8)"] = st.number_input("C8", min_value=0.0, max_value=1.0, value=0.07, step=0.01)
        
        if st.form_submit_button("Simpan Preferensi"):
            if sum(weights.values()) == 1:
                st.success("Preferensi tersimpan")
            else:
                st.error("Total semua bobot harus sama dengan 1!")

st.subheader("Seleksi Warga Penerima Bantuan Sosial")

# Input jumlah penerima bantuan
n = st.number_input("Masukkan jumlah penerima bantuan:", min_value=1, max_value=len(df), value=10, step=1)
if n > len(df):
    st.error("Jumlah penerima bantuan melebihi jumlah penduduk!")

if st.button("Seleksi Penerima Bansos"):
    # Perhitungan skor TOPSIS
    topsis_scores = calculate_topsis(df)
    df["TOPSIS Score"] = topsis_scores

    # Peringkat berdasarkan skor TOPSIS
    df_sorted_topsis = df.sort_values(by="TOPSIS Score", ascending=False)

    # Menampilkan hasil penerima bansos berdasarkan pemeringkatan
    st.subheader("Penerima Bantuan Sosial Berdasarkan Metode TOPSIS")
    st.dataframe(df_sorted_topsis[["Nama", "TOPSIS Score"]].head(n))