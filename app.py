import streamlit as st
import math

st.set_page_config(page_title="Farm Ventilation PRO", layout="centered")

st.title("🐷🐔 Farm Ventilation Calculator (BESS Version)")

# ----------------------
# SECTION 1: HOUSE
# ----------------------
st.header("1️⃣ ข้อมูลโรงเรือน")

width = st.number_input("ความกว้างโรงเรือน (m)", value=12.0)
height = st.number_input("ความสูงโรงเรือน (m)", value=3.0)

# ----------------------
# SECTION 2: AIR SPEED
# ----------------------
st.header("2️⃣ ความเร็วลม")

unit = st.selectbox("หน่วยความเร็วลม", ["m/s", "ft/min"])

air_speed_input = st.number_input("ความเร็วลม", value=2.5)

# convert unit
if unit == "ft/min":
    air_speed = air_speed_input / 196.85
else:
    air_speed = air_speed_input

# show conversion
st.caption(f"≈ {air_speed:.2f} m/s | {air_speed * 196.85:.0f} ft/min")

# ----------------------
# SECTION 3: COOLING PAD (INPUT ก่อนคำนวณ)
# ----------------------
st.header("3️⃣ Cooling Pad")

pad_height = st.selectbox("ความสูง Pad (m)", [1.5, 1.8, 2.0, 2.4])
pad_width = st.selectbox("ความกว้างต่อก้อน (m)", [0.6, 0.3])

# ----------------------
# SECTION 4: FAN (BESS)
# ----------------------
st.header("4️⃣ พัดลม (อ้างอิง BESS Lab)")

fan_capacity = st.number_input(
    "กำลังพัดลม (m³/hr จาก BESS)", value=38000.0
)

# ----------------------
# SECTION 5: PUMP
# ----------------------
st.header("5️⃣ Pump")

water_rate = st.selectbox("Water Rate (L/min/m²)", [6, 7, 8, 9, 10])

# ----------------------
# CALCULATION
# ----------------------
if st.button("คำนวณทั้งหมด"):

    st.header("📊 ผลลัพธ์")

    # ----------------------
    # AIRFLOW
    # ----------------------
    area = width * height
    airflow = area * air_speed * 3600

    # ----------------------
    # FAN
    # ----------------------
    num_fans = math.ceil(airflow / fan_capacity)

    # ----------------------
    # COOLING PAD AREA
    # ----------------------
    pad_area = airflow / 10000

    pad_per_piece = pad_height * pad_width
    num_pads = math.ceil(pad_area / pad_per_piece)
    total_length = num_pads * pad_width

    # ----------------------
    # PUMP
    # ----------------------
    pump_lpm = pad_area * water_rate
    pump_m3hr = (pump_lpm * 60) / 1000
    pump_safe = pump_m3hr * 1.2

    # ----------------------
    # OUTPUT
    # ----------------------
    st.subheader("🌬️ ระบบลม")
    st.write(f"Airflow: {airflow:,.0f} m³/hr")
    st.write(f"จำนวนพัดลม: {num_fans} ตัว")

    st.subheader("🧊 Cooling Pad")
    st.write(f"พื้นที่ Pad: {pad_area:.2f} m²")
    st.write(f"พื้นที่ต่อก้อน: {pad_per_piece:.2f} m²")
    st.write(f"จำนวนก้อน: {num_pads} ก้อน")
    st.write(f"ความยาวรวม: {total_length:.2f} m")

    st.subheader("💧 Pump")
    st.write(f"Flow: {pump_lpm:,.0f} L/min")
    st.write(f"Pump Size: {pump_m3hr:.2f} m³/hr")
    st.write(f"Pump (เผื่อ 20%): {pump_safe:.2f} m³/hr")
