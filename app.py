import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="MindFlow - Catatan Mood Harian", layout="wide")
st.title("🧠 MindFlow - Catatan Mood dan Usaha Belajar Harian")

# Load data CSV atau inisialisasi
CSV_FILE = "mindflow_data.csv"
try:
    df = pd.read_csv(CSV_FILE)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
except:
    df = pd.DataFrame(columns=["Tanggal", "USD", "Catatan"])

# Input data baru
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        usd_value = st.number_input("Berapa nilai usaha dan perasaan hari ini? (pakai USD)", min_value=0.0, step=0.5)
    with col2:
        catatan = st.text_area("Bagaimana kamu hari ini dan proses belajarnya?")
    submitted = st.form_submit_button("Simpan")

    if submitted:
        new_data = pd.DataFrame([{"Tanggal": datetime.now(), "USD": usd_value, "Catatan": catatan}])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Data berhasil disimpan!")

# Tampilkan grafik
st.subheader("📊 Grafik Nilai Harian")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Tanggal"], y=df["USD"], mode='lines+markers', name='Mood USD'))
st.plotly_chart(fig, use_container_width=True)

# Persentase perubahan
if len(df) >= 2:
    harian = ((df.iloc[-1]["USD"] - df.iloc[-2]["USD"]) / df.iloc[-2]["USD"]) * 100
else:
    harian = None

st.markdown("**📈 Perubahan Nilai:**")
st.markdown(f"- Harian: {harian:.2f}%" if harian is not None else "- Harian: N/A")
st.markdown("- Mingguan: N/A")
st.markdown("- Bulanan: N/A")

# Riwayat & catatan dengan opsi baca selengkapnya
st.subheader("📅 Riwayat Nilai dan Catatan")
for i, row in df[::-1].iterrows():
    with st.expander(f"{row['Tanggal'].strftime('%Y-%m-%d %H:%M:%S')} - ${row['USD']:.2f}"):
        st.write(row['Catatan'])

# --- Setup Database ---
conn = sqlite3.connect('mindflow.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS mood_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    usd_value REAL,
    notes TEXT
)
''')
conn.commit()

# --- Input Form ---
st.title("🧠 MindFlow Tracker")
with st.form("mood_form"):
    usd_value = st.slider("Berapa nilai kamu hari ini (USD analogi)?", 0.0, 10.0, 1.0, step=0.5)
    notes = st.text_area("Bagaimana kamu hari ini dan proses belajarnya?")
    submit = st.form_submit_button("💾 Simpan Data")

if submit:
    cursor.execute("INSERT INTO mood_log (timestamp, usd_value, notes) VALUES (?, ?, ?)",
                   (datetime.now().isoformat(), usd_value, notes))
    conn.commit()
    st.success("✅ Catatan berhasil disimpan!")

# --- Tampilkan Data ---
st.subheader("📊 Riwayat Mood")
df = pd.read_sql_query("SELECT * FROM mood_log", conn)
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.dataframe(df[["timestamp", "usd_value", "notes"]].sort_values("timestamp", ascending=False))

    # --- Chart ---
    fig = px.line(df, x='timestamp', y='usd_value', title='Perkembangan Nilai Mood')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Belum ada data, silakan isi dulu.")

