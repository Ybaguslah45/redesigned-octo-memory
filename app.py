import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="MindFlow - Catatan Mood Harian", layout="wide")
st.title("🧠 MindFlow - Catatan Mood dan Usaha Belajar Harian")

# Load data CSV atau inisialisasi
CSV_FILE = "mindflow_data.csv"
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
else:
    df = pd.DataFrame(columns=["Tanggal", "USD", "Catatan"])

# Input data baru
if "usd_value" not in st.session_state:
    st.session_state.usd_value = 0.0
if "catatan" not in st.session_state:
    st.session_state.catatan = ""

with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        usd_value = st.text_input("Nilai (USD):", value="" if st.session_state.usd_value == 0.0 else str(st.session_state.usd_value))
    with col2:
        catatan = st.text_area("Catatan Hari Ini:", value=st.session_state.catatan)
    submitted = st.form_submit_button("Simpan")

    if submitted:
        try:
            usd_val = float(usd_value)
            new_data = pd.DataFrame([{"Tanggal": datetime.now(), "USD": usd_val, "Catatan": catatan}])
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ Data berhasil disimpan!")
            st.session_state.usd_value = 0.0
            st.session_state.catatan = ""
        except ValueError:
            st.error("❌ Masukkan angka yang valid untuk nilai USD.")

# Tampilkan grafik
st.subheader("📊 Grafik Nilai Harian")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Tanggal"], y=df["USD"], mode='lines+markers', name='Mood USD'))
st.plotly_chart(fig, use_container_width=True)

# Persentase perubahan
st.subheader("📈 Perubahan Nilai")
if len(df) >= 2:
    now = df.iloc[-1]["USD"]
    prev = df.iloc[-2]["USD"]
    if prev != 0:
        harian = ((now - prev) / prev) * 100
    else:
        harian = float("inf")
    st.markdown(f"- Harian: {harian:+.2f}%")
else:
    st.markdown("- Harian: N/A")

st.markdown("- Mingguan: N/A")
st.markdown("- Bulanan: N/A")

# Riwayat & catatan dengan opsi baca selengkapnya dan tombol delete
st.subheader("📅 Riwayat Nilai dan Catatan")
if not df.empty:
    for i in reversed(df.index):
        row = df.loc[i]
        with st.expander(f"{row['Tanggal'].strftime('%Y-%m-%d %H:%M:%S')} - ${row['USD']:.2f}"):
            st.write(row['Catatan'])
            if st.button(f"🗑️ Hapus catatan ini", key=f"delete_{i}"):
                df = df.drop(i).reset_index(drop=True)
                df.to_csv(CSV_FILE, index=False)
                st.experimental_rerun()
else:
    st.info("Belum ada data yang disimpan.")
