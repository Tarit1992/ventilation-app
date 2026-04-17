import streamlit as st
import math

st.set_page_config(page_title="Farm Ventilation PRO", layout="centered")

st.title("🐷🐔 Farm Ventilation Calculator (CFM + BESS)")

# ----------------------
# SECTION 1: INPUT
# ----------------------
st.header("1️⃣ ข้อมูลโรงเรือน")

width_m = st.number_input("ความกว้าง (m)", value=18.0)
height_m = st.number_input("ความสูง (m)", value=3.0)
air_speed_fpm = st.number_input("Air Speed (ft/min)", value=800.0)

# ----------------------
# SECTION 2: FAN
# ----------------------
st.header("2️⃣ พัดลม (BESS)")

fan_cfm = st.number_input("กำลังพัดลม (CFM จาก BESS)", value=25000.0)

# ----------------------
# SECTION 3: COOLING PAD
# ----------------------
st.header("3️⃣ Cooling Pad")

pad_height = st.selectbox("ความสูง Pad (m)", [1.5, 1.8, 2.0, 2.4])
pad_width = st.selectbox("ความกว้าง Pad (m)", [0.6, 0.3])

# ----------------------
# CALCULATION
# ----------------------
if st.button("คำนวณทั้งหมด"):

    st.header("📊 ผลลัพธ์")

    # ----------------------
    # CFM (สูตรคุณ)
    # ----------------------
    width_ft = width_m * 3.28084
    height_ft = height_m * 3.28084
    area_ft2 = width_ft * height_ft

    cfm = area_ft2 * air_speed_fpm
    m3hr = cfm * 1.699

    st.subheader("🌬️ ระบบลม")
    st.write(f"พื้นที่หน้าตัด: {area_ft2:,.0f} ft²")
    st.write(f"Airflow: {cfm:,.0f} CFM")
    st.write(f"Airflow: {m3hr:,.0f} m³/hr")

    # ----------------------
    # FAN
    # ----------------------
    num_fans = math.ceil(cfm / fan_cfm)
    st.write(f"จำนวนพัดลม: {num_fans} ตัว")

    # ----------------------
    # COOLING PAD
    # ----------------------
    st.subheader("🧊 Cooling Pad")

    pad_area = m3hr / 10000  # m²

    pad_per_piece = pad_height * pad_width
    num_pads = math.ceil(pad_area / pad_per_piece)
    total_length = num_pads * pad_width

    st.write(f"พื้นที่ Pad: {pad_area:.2f} m²")
    st.write(f"พื้นที่ต่อก้อน: {pad_per_piece:.2f} m²")
    st.write(f"จำนวนก้อน: {num_pads} ก้อน")
    st.write(f"ความยาวรวม: {total_length:.2f} m")

    # ----------------------
    # PUMP (ตามที่คุณกำหนด)
    # ----------------------
    st.subheader("💧 Pump")

    # 기준: 1 แผ่น (1.8 x 0.6) ใช้ 7 L/min
    base_pad_area = 1.8 * 0.6  # 1.08 m²
    base_flow = 7  # L/min

    # หา L/min ต่อ m²
    flow_per_m2 = base_flow / base_pad_area

    # คำนวณปั๊มจากพื้นที่จริง
    pump_lpm = pad_area * flow_per_m2

    # เผื่อ 20%
    pump_lpm_safe = pump_lpm * 1.2

    st.write(f"อัตราน้ำต่อ m²: {flow_per_m2:.2f} L/min/m²")
    st.write(f"Flow ปั๊ม: {pump_lpm:,.0f} L/min")
    st.write(f"Pump (เผื่อ 20%): {pump_lpm_safe:,.0f} L/min")
