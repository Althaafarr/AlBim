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


# Lima pilihan sensor umum untuk setiap variabel. Nilai noise dan resolusi
# digunakan untuk simulasi edukasi, bukan klaim spesifikasi/kalibrasi resmi.
SENSOR_OPTIONS = {
    "Suhu": {
        "DS18B20": (0.25, 0.0625, "Sensor suhu digital"),
        "LM35": (0.40, 0.10, "Sensor suhu analog"),
        "DHT22 / AM2302": (0.50, 0.10, "Sensor suhu dan kelembapan"),
        "Termokopel tipe K + MAX6675": (0.75, 0.25, "Termokopel rentang suhu luas"),
        "PT100 + MAX31865": (0.20, 0.10, "Sensor suhu RTD"),
    },
    "Tekanan": {
        "BMP280": (80.0, 1.0, "Sensor tekanan barometrik"),
        "BME280": (100.0, 1.0, "Sensor tekanan, suhu, dan kelembapan"),
        "MPX5700": (1500.0, 100.0, "Sensor tekanan analog"),
        "Transduser tekanan 0–1 bar (4–20 mA)": (1200.0, 100.0, "Transduser tekanan industri"),
        "Transduser tekanan 0–10 bar": (2500.0, 500.0, "Transduser tekanan rentang lebih tinggi"),
    },
    "Arus listrik": {
        "ACS712": (0.035, 0.01, "Sensor arus Hall-effect"),
        "INA219": (0.008, 0.001, "Monitor arus dan tegangan DC"),
        "INA226": (0.004, 0.001, "Monitor arus dan tegangan DC"),
        "SCT-013": (0.05, 0.01, "Transformator arus AC"),
        "ACS758": (0.045, 0.01, "Sensor arus Hall-effect rentang tinggi"),
    },
    "Tegangan listrik": {
        "Pembagi tegangan (voltage divider)": (0.15, 0.01, "Pengukuran tegangan DC melalui pembagi"),
        "INA219": (0.025, 0.01, "Monitor tegangan dan arus DC"),
        "INA226": (0.015, 0.001, "Monitor tegangan dan arus DC"),
        "ZMPT101B": (0.50, 0.10, "Modul sensor tegangan AC"),
        "PZEM-004T": (0.35, 0.10, "Modul pengukuran listrik AC"),
    },
    "Daya listrik": {
        "PZEM-004T": (2.0, 1.0, "Modul pengukuran daya listrik AC"),
        "INA219": (0.5, 0.1, "Daya DC dihitung dari tegangan dan arus"),
        "INA226": (0.3, 0.1, "Daya DC dihitung dari tegangan dan arus"),
        "PZEM-016": (2.5, 1.0, "Meter listrik AC"),
        "Modul ADE7753": (1.5, 0.1, "IC pengukuran energi dan daya"),
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

def simulate_value(variable, sample_no, sensor_name):
    cfg = CONFIG[variable]
    noise_limit, resolution, _description = SENSOR_OPTIONS[variable][sensor_name]
    trend = (sample_no - 1) * cfg["variation"] * 0.08
    noise = random.uniform(-noise_limit, noise_limit)
    value = max(cfg["min"], min(cfg["max"], cfg["base"] + trend + noise))
    return round(round(value / resolution) * resolution, 6)

st.title("📟 Smart Measurement System")
st.caption("Dashboard simulasi pengukuran, konversi satuan, tabel, dan grafik.")
st.caption("Dibuat oleh Althaaf Ar Rachman dan Muhammad Bima At-Taki.")
st.warning(
    "MODE SIMULASI: nilai dibuat program, bukan berasal dari sensor fisik. Pilihan sensor mengubah noise dan resolusi simulasi; angka karakteristik hanya ilustrasi edukasi."
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
    sensor_name = st.selectbox("Pilih sensor", list(SENSOR_OPTIONS[variable].keys()), key=f"sensor_{variable}")
    noise_limit, sensor_resolution, sensor_description = SENSOR_OPTIONS[variable][sensor_name]
    st.caption(f"{sensor_description} · Noise simulasi ±{noise_limit} {cfg['source_unit']} · Resolusi simulasi {sensor_resolution} {cfg['source_unit']}")
    st.write(f"**Satuan sumber:** {cfg['source_unit']}")
    target_unit = st.selectbox("Satuan keluaran", cfg["units"], key=f"unit_{variable}")
    sample_count = st.number_input("Jumlah sampel", min_value=1, max_value=500, value=10, step=1)
    interval_value = st.number_input("Interval antarsampel", min_value=0.1, max_value=1440.0, value=1.0, step=0.5)
    interval_unit = st.selectbox("Satuan interval", ["Detik", "Menit"], key=f"interval_unit_{variable}")
    interval_seconds = float(interval_value) * (60.0 if interval_unit == "Menit" else 1.0)
    duration_value = st.number_input("Durasi maksimum", min_value=0.1, max_value=1440.0, value=15.0, step=1.0)
    duration_unit = st.selectbox("Satuan durasi maksimum", ["Detik", "Menit"], key=f"duration_unit_{variable}")
    duration_seconds = float(duration_value) * (60.0 if duration_unit == "Menit" else 1.0)
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
              Sensor simulasi: {sensor_name} • Satuan sumber {cfg['source_unit']} • Keluaran {target_unit}
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
        scheduled_elapsed = (i - 1) * interval_seconds
        if scheduled_elapsed > duration_seconds:
            break
        if realtime and i > 1:
            time.sleep(interval_seconds)
        elapsed = time.monotonic() - start if realtime else scheduled_elapsed
        if elapsed > duration_seconds:
            break

        raw = simulate_value(variable, i, sensor_name)
        converted = convert(raw, variable, target_unit)
        records.append({
            "Nomor sampel": i,
            "Waktu (detik)": round(elapsed, 3),
            "Waktu (menit)": round(elapsed / 60.0, 4),
            "Variabel": variable,
            "Sensor": sensor_name,
            "Noise simulasi": noise_limit,
            "Resolusi simulasi": sensor_resolution,
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
    st.session_state.last_sensor = sensor_name
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


st.markdown("---")
st.markdown(
    """<div style="text-align:center;padding:8px 0;color:#64748b;">
    <div>Smart Measurement System</div>
    <div style="font-weight:600;">Dibuat oleh Althaaf Ar Rachman dan Muhammad Bima At-Taki</div>
    </div>""",
    unsafe_allow_html=True,
)