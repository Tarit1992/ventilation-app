import streamlit as st
import math

st.set_page_config(page_title="Farm Ventilation Pro", layout="centered")

st.title("🐷🐔 Farm Ventilation Calculator PRO")

# ----------------------
# SECTION 1: INPUT
# ----------------------
st.header("1️⃣ ข้อมูลโรงเรือน")

width = st.number_input("ความกว้างโรงเรือน (m)", value=12.0)
height = st.number_input("ความสูงโรงเรือน (m)", value=3.0)

# ----------------------
# AIR SPEED
# ----------------------
st.header("2️⃣ ความเร็วลม")

unit = st.selectbox("หน่วยความเร็วลม", ["m/s", "ft/min"])

air_speed_input = st.number_input("ความเร็วลม", value=2.5)

# แปลงหน่วย
if unit == "ft/min":
    air_speed = air_speed_input / 196.85
else:
    air_speed = air_speed_input

# แสดงค่าเทียบ
air_speed_ft = air_speed * 196.85
st.caption(f"≈ {air_speed:.2f} m/s | {air_speed_ft:.0f} ft/min")

# ----------------------
# FAN
# ----------------------
st.header("3️⃣ พัดลม")

fan_capacity = st.number_input(
    "กำลังพัดลม (m³/hr @ 0.15 in.w.g.)", value=40000.0
)

pressure = st.selectbox(
    "Static Pressure (inch water gauge)",
    [0.15, 0.2, 0.3]
)

pressure_factor = {
    0.15: 1.00,
    0.2: 0.92,
    0.3: 0.85
}

# ----------------------
# CALCULATION
# ----------------------
if st.button("คำนวณทั้งหมด"):

    st.header("📊 ผลลัพธ์ระบบลม")

    # พื้นที่หน้าตัด
    area = width * height

    # airflow
    airflow = area * air_speed * 3600

    # ปรับ fan ตาม pressure
    adjusted_fan = fan_capacity * pressure_factor[pressure]

    num_fans = math.ceil(airflow / adjusted_fan)

    # pad
    pad_area = airflow / 10000

    st.write(f"Airflow: {airflow:,.0f} m³/hr")
    st.write(f"Fan Capacity (adjusted): {adjusted_fan:,.0f} m³/hr")
    st.write(f"จำนวนพัดลม: {num_fans} ตัว")
    st.write(f"Cooling Pad Area: {pad_area:.2f} m²")

    # ----------------------
    # PAD SELECTION
    # ----------------------
    st.header("🧊 Cooling Pad")

    pad_height = st.selectbox("ความสูง Pad (m)", [1.5, 1.8, 2.0, 2.4])
    pad_width = st.selectbox("ความกว้าง Pad (m)", [0.6, 0.3])

    pad_per_piece = pad_height * pad_width
    num_pads = math.ceil(pad_area / pad_per_piece)
    total_length = num_pads * pad_width

    st.write(f"พื้นที่ต่อก้อน: {pad_per_piece:.2f} m²")
    st.write(f"จำนวน Pad: {num_pads} ก้อน")
    st.write(f"ความยาวรวม: {total_length:.2f} m")

    # ----------------------
    # PUMP
    # ----------------------
    st.header("💧 Pump")

    water_rate = st.selectbox("Water Rate (L/min/m²)", [6, 7, 8, 9, 10])

    pump_lpm = pad_area * water_rate
    pump_m3hr = (pump_lpm * 60) / 1000
    pump_safe = pump_m3hr * 1.2

    st.write(f"Flow: {pump_lpm:,.0f} L/min")
    st.write(f"Pump Size: {pump_m3hr:.2f} m³/hr")
    st.write(f"Pump (เผื่อ 20%): {pump_safe:.2f} m³/hr")

    st.info(f"Static Pressure: {pressure} in.w.g.")
