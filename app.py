import time
import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Smart Measurement System",
    page_icon="📟",
    layout="wide",
)

CONFIG = {
    "Suhu": {
        "icon": "🌡️",
        "sensor": "Ilustrasi sensor suhu",
        "source_unit": "°C",
        "units": ["°C", "°F", "K"],
        "base": 25.0,
        "variation": 2.0,
        "min": -50.0,
        "max": 150.0,
        "description": "Memantau perubahan suhu.",
    },
    "Tekanan": {
        "icon": "🧭",
        "sensor": "Ilustrasi sensor tekanan",
        "source_unit": "Pa",
        "units": ["Pa", "kPa", "bar"],
        "base": 101325.0,
        "variation": 500.0,
        "min": 0.0,
        "max": 2_000_000.0,
        "description": "Memantau tekanan fluida atau gas.",
    },
    "Arus listrik": {
        "icon": "🔌",
        "sensor": "Ilustrasi sensor arus",
        "source_unit": "A",
        "units": ["A", "mA"],
        "base": 2.0,
        "variation": 0.5,
        "min": 0.0,
        "max": 100.0,
        "description": "Memantau arus listrik.",
    },
    "Tegangan listrik": {
        "icon": "⚡",
        "sensor": "Ilustrasi sensor tegangan",
        "source_unit": "V",
        "units": ["V", "mV"],
        "base": 12.0,
        "variation": 1.0,
        "min": 0.0,
        "max": 1000.0,
        "description": "Memantau tegangan listrik.",
    },
    "Daya listrik": {
        "icon": "📈",
        "sensor": "Ilustrasi sensor daya",
        "source_unit": "W",
        "units": ["W", "kW"],
        "base": 24.0,
        "variation": 4.0,
        "min": 0.0,
        "max": 100_000.0,
        "description": "Memantau daya listrik.",
    },
}

def convert(value, variable, target):
    source = CONFIG[variable]["source_unit"]
    if source == target:
        return value
    rules = {
        ("Suhu", "°C", "°F"): lambda x: x * 9 / 5 + 32,
        ("Suhu", "°C", "K"): lambda x: x + 273.15,
        ("Tekanan", "Pa", "kPa"): lambda x: x / 1000,
        ("Tekanan", "Pa", "bar"): lambda x: x / 100000,
        ("Arus listrik", "A", "mA"): lambda x: x * 1000,
        ("Tegangan listrik", "V", "mV"): lambda x: x * 1000,
        ("Daya listrik", "W", "kW"): lambda x: x / 1000,
    }
    fn = rules.get((variable, source, target))
    if fn is None:
        raise ValueError("Konversi satuan tidak tersedia.")
    return fn(value)

def simulate_value(variable, sample_no):
    cfg = CONFIG[variable]
    trend = (sample_no - 1) * cfg["variation"] * 0.08
    noise = random.uniform(-cfg["variation"], cfg["variation"])
    return max(cfg["min"], min(cfg["max"], cfg["base"] + trend + noise))

st.title("📟 Smart Measurement System")
st.caption("Dashboard simulasi pengukuran, konversi satuan, tabel, dan grafik.")
st.warning(
    "MODE SIMULASI: nilai yang ditampilkan dibuat oleh program, bukan berasal dari sensor fisik. "
    "Ilustrasi di kartu hanya mewakili jenis pengukuran, bukan model sensor tertentu."
)

# Cards as visual selector
st.subheader("1. Pilih variabel pengukuran")
cols = st.columns(5)
variable_names = list(CONFIG.keys())
if "variable" not in st.session_state:
    st.session_state.variable = "Suhu"

for col, name in zip(cols, variable_names):
    cfg = CONFIG[name]
    with col:
        st.markdown(
            f"""
            <div style="border:1px solid #d7dee8;border-radius:14px;padding:14px;
                        min-height:130px;text-align:center;background:#f8fafc;color:#172033">
                <div style="font-size:34px">{cfg['icon']}</div>
                <div style="font-weight:700">{name}</div>
                <div style="font-size:12px;color:#5b6575;margin-top:6px">{cfg['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Pilih {name}", key=f"select_{name}", use_container_width=True):
            st.session_state.variable = name

variable = st.session_state.variable
cfg = CONFIG[variable]

st.markdown("---")
left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("2. Pengaturan pengukuran")
    st.markdown(f"### {cfg['icon']} {variable}")
    st.write(f"**Sensor:** {cfg['sensor']} (simulasi)")
    st.write(f"**Satuan sumber:** {cfg['source_unit']}")
    target_unit = st.selectbox("Satuan keluaran", cfg["units"], key=f"unit_{variable}")
    sample_count = st.number_input("Jumlah sampel", min_value=1, max_value=500, value=10, step=1)
    interval = st.number_input("Interval antarsampel (detik)", min_value=0.1, max_value=3600.0, value=1.0, step=0.5)
    duration = st.number_input("Durasi maksimum (detik)", min_value=0.1, max_value=3600.0, value=15.0, step=1.0)
    realtime = st.checkbox("Jalankan sesuai waktu nyata (menunggu antar sampel)", value=False)
    run_button = st.button("▶ Mulai simulasi", type="primary", use_container_width=True)
    reset_button = st.button("↻ Reset hasil", use_container_width=True)

with right:
    st.subheader("3. Ilustrasi dan status")
    st.markdown(
        f"""
        <div style="display:flex;gap:18px;align-items:center;border:1px solid #d7dee8;
                    border-radius:16px;padding:20px;background:#f8fafc;color:#172033">
          <div style="font-size:76px">{cfg['icon']}</div>
          <div>
            <div style="font-size:23px;font-weight:750">{variable}</div>
            <div style="margin-top:6px">{cfg['description']}</div>
            <div style="margin-top:8px;font-size:13px;color:#5b6575">
              Model sensor simulasi • Satuan sumber {cfg['source_unit']} • Keluaran {target_unit}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Alur kerja: pilih variabel → atur parameter → ambil sampel → konversi → "
        "tampilkan tabel dan grafik. Setelah tipe sensor nyata ditentukan, ilustrasi dan fungsi "
        "pembacaan dapat disesuaikan dengan perangkat sebenarnya."
    )

if reset_button:
    st.session_state.pop("records", None)
    st.session_state.pop("last_variable", None)
    st.rerun()

if run_button:
    records = []
    start = time.monotonic()
    progress = st.progress(0, text="Menyiapkan simulasi...")
    status = st.empty()
    for i in range(1, int(sample_count) + 1):
        scheduled_elapsed = (i - 1) * float(interval)
        if scheduled_elapsed > float(duration):
            break
        if realtime and i > 1:
            time.sleep(float(interval))
        elapsed = time.monotonic() - start if realtime else scheduled_elapsed
        if elapsed > float(duration):
            break

        raw = simulate_value(variable, i)
        converted = convert(raw, variable, target_unit)
        records.append({
            "Nomor sampel": i,
            "Waktu (detik)": round(elapsed, 3),
            "Variabel": variable,
            "Sensor": cfg["sensor"],
            "Nilai asli": raw,
            "Satuan asli": cfg["source_unit"],
            "Nilai konversi": converted,
            "Satuan keluaran": target_unit,
            "Status": "Valid",
        })
        progress.progress(i / int(sample_count), text=f"Mengambil sampel {i}/{int(sample_count)}")
        status.caption(f"Sampel {i}: {raw:.4f} {cfg['source_unit']} → {converted:.4f} {target_unit}")

    st.session_state.records = records
    st.session_state.last_variable = variable
    st.session_state.last_unit = target_unit
    st.success(f"Simulasi selesai. Data valid terkumpul: {len(records)} dari target {int(sample_count)}.")

records = st.session_state.get("records", [])
if records:
    st.markdown("---")
    st.subheader("4. Ringkasan hasil")
    df = pd.DataFrame(records)
    vals = df["Nilai konversi"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sampel valid", len(df))
    m2.metric("Minimum", f"{vals.min():.3f} {st.session_state.last_unit}")
    m3.metric("Maksimum", f"{vals.max():.3f} {st.session_state.last_unit}")
    m4.metric("Rata-rata", f"{vals.mean():.3f} {st.session_state.last_unit}")

    st.subheader("5. Grafik pengukuran")
    chart_df = df.rename(columns={"Nilai konversi": f"Nilai ({st.session_state.last_unit})"})
    y_col = f"Nilai ({st.session_state.last_unit})"
    fig = px.line(
        chart_df,
        x="Waktu (detik)",
        y=y_col,
        markers=True,
        title=f"{st.session_state.last_variable} terhadap waktu",
    )
    fig.update_layout(height=420, margin=dict(l=15, r=15, t=60, b=15))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("6. Tabel data")
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇ Unduh data CSV",
        data=csv_data,
        file_name="hasil_pengukuran_simulasi.csv",
        mime="text/csv",
    )
else:
    st.markdown("---")
    st.subheader("4. Hasil pengukuran")
    st.write("Belum ada data. Pilih variabel, atur parameter, lalu tekan **Mulai simulasi**.")
