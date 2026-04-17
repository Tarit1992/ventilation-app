import streamlit as st

st.set_page_config(page_title="Farm Ventilation Pro", layout="centered")

st.title("🐷🐔 Ventilation Calculator PRO")

# ----------------------
# INPUT
# ----------------------
width = st.number_input("ความกว้าง (m)", value=12.0)
height = st.number_input("ความสูง (m)", value=3.0)

# เลือกหน่วยลม
unit = st.selectbox("หน่วยความเร็วลม", ["m/s", "ft/s"])

air_speed = st.number_input("ความเร็วลม", value=2.5)

# แปลง ft/s → m/s
if unit == "ft/s":
    air_speed = air_speed * 0.3048

fan_capacity = st.number_input("กำลังพัดลม (m3/hr @ 0.15 in.w.g.)", value=40000.0)

# Static Pressure
pressure = st.selectbox(
    "Static Pressure (inch water gauge)",
    [0.15, 0.2, 0.3]
)

# Efficiency factor ตาม pressure
pressure_factor = {
    0.15: 1.00,
    0.2: 0.92,
    0.3: 0.85
}

# ----------------------
# CALCULATION
# ----------------------
if st.button("คำนวณ"):
    area = width * height
    airflow = area * air_speed * 3600

    # ปรับพัดลมตาม pressure
    adjusted_fan_capacity = fan_capacity * pressure_factor[pressure]

    num_fans = airflow / adjusted_fan_capacity
    pad_area = airflow / 10000

    # ----------------------
    # OUTPUT
    # ----------------------
    st.success("ผลลัพธ์")

    st.write(f"Airflow: {airflow:,.0f} m³/hr")
    st.write(f"กำลังพัดลม (หลังหัก pressure): {adjusted_fan_capacity:,.0f} m³/hr")

    st.write(f"จำนวนพัดลม: {round(num_fans)} ตัว")
    st.write(f"Cooling Pad: {pad_area:.2f} m²")

    st.info(f"ใช้ Static Pressure: {pressure} in.w.g.")
