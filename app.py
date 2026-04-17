import streamlit as st
import math

st.set_page_config(page_title="Farm Ventilation PRO", layout="centered")

st.title("🐷🐔 Farm Ventilation Calculator PRO")

# ----------------------
# INPUT
# ----------------------
st.header("1️⃣ ข้อมูลโรงเรือน")

width_m = st.number_input("ความกว้าง (m)", value=18.0)
height_m = st.number_input("ความสูง (m)", value=3.0)
air_speed_fpm = st.number_input("Air Speed (ft/min)", value=800.0)

# ----------------------
# FAN
# ----------------------
st.header("2️⃣ พัดลม")

fan_cfm = st.number_input("กำลังพัดลมต่อ 1 ตัว (CFM)", value=25000.0)

# ----------------------
# PAD
# ----------------------
st.header("3️⃣ Cooling Pad")

pad_height = st.selectbox("ความสูง Pad (m)", [1.5, 1.8, 2.0, 2.4])
pad_width = st.selectbox("ความกว้าง Pad (m)", [0.6, 0.3])

layout = st.radio(
    "รูปแบบติดตั้ง Pad",
    ["2 ด้าน (ซ้าย-ขวา)", "3 ด้าน (ซ้าย-ขวา-หน้า)"]
)

front_length = 0
if layout == "3 ด้าน (ซ้าย-ขวา-หน้า)":
    front_length = st.number_input("ความยาว Pad ด้านหน้า (m)", value=10.0)

# ----------------------
# CALCULATION
# ----------------------
if st.button("คำนวณทั้งหมด"):

    st.header("📊 ผลลัพธ์")

    # ----------------------
    # CFM
    # ----------------------
    width_ft = width_m * 3.28084
    height_ft = height_m * 3.28084
    area_ft2 = width_ft * height_ft

    required_cfm = area_ft2 * air_speed_fpm
    m3hr = required_cfm * 1.699

    st.subheader("🌬️ ความต้องการลม")
    st.write(f"ต้องการลม: {required_cfm:,.0f} CFM")

    # ----------------------
    # FAN
    # ----------------------
    num_fans = math.ceil(required_cfm / fan_cfm)
    total_fan_cfm = num_fans * fan_cfm

    st.subheader("🌀 พัดลม")
    st.write(f"จำนวนพัดลม: {num_fans} ตัว")
    st.write(f"ลมรวมจากพัดลม: {total_fan_cfm:,.0f} CFM")

    if total_fan_cfm >= required_cfm:
        st.success("✔ พัดลมเพียงพอ")
    else:
        st.error("❌ พัดลมไม่พอ")

    # ----------------------
    # PAD AREA
    # ----------------------
    pad_area = m3hr / 10000

    st.subheader("🧊 Cooling Pad")

    st.write(f"พื้นที่ Pad ที่ต้องใช้: {pad_area:.2f} m²")

    # ความยาว pad รวม
    total_pad_length = pad_area / pad_height

    # ----------------------
    # LAYOUT
    # ----------------------
    if layout == "2 ด้าน (ซ้าย-ขวา)":
        side_length = total_pad_length / 2
        front_length = 0

        st.write(f"ความยาว Pad ต่อด้าน (ซ้าย/ขวา): {side_length:.2f} m")

        side_lengths = [side_length, side_length]

    else:
        remaining = total_pad_length - front_length

        if remaining < 0:
            st.error("❌ ความยาวด้านหน้ามากเกินไป")
            remaining = 0

        side_length = remaining / 2

        st.write(f"ด้านหน้า: {front_length:.2f} m")
        st.write(f"ซ้าย/ขวา: {side_length:.2f} m ต่อด้าน")

        side_lengths = [side_length, side_length, front_length]

    # ----------------------
    # PAD PIECES
    # ----------------------
    pad_per_piece = pad_height * pad_width
    num_pads = math.ceil(pad_area / pad_per_piece)

    st.write(f"จำนวนก้อนทั้งหมด: {num_pads} ก้อน")

    # ----------------------
    # PUMP
    # ----------------------
    st.subheader("💧 Pump")

    # 기준: 1.8x0.6 = 7 L/min
    base_area = 1.8 * 0.6
    flow_per_m2 = 7 / base_area

    pumps = []

    for i, length in enumerate(side_lengths):
        area_side = length * pad_height
        flow = area_side * flow_per_m2
        flow_safe = flow * 1.2

        pumps.append(flow_safe)

        st.write(f"ด้านที่ {i+1}: {flow_safe:,.0f} L/min")

    st.write(f"จำนวนปั๊มทั้งหมด: {len(pumps)} ตัว")
