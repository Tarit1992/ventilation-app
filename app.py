import streamlit as st

st.set_page_config(page_title="Farm Ventilation", layout="centered")

st.title("🐷🐔 Ventilation Calculator")

width = st.number_input("ความกว้าง (m)", value=12.0)
height = st.number_input("ความสูง (m)", value=3.0)
air_speed = st.number_input("ความเร็วลม (m/s)", value=2.5)
fan_capacity = st.number_input("กำลังพัดลม (m3/hr)", value=40000.0)

if st.button("คำนวณ"):
    area = width * height
    airflow = area * air_speed * 3600
    fans = airflow / fan_capacity
    pad = airflow / 10000

    st.success("ผลลัพธ์")
    st.write(f"Airflow: {airflow:,.0f} m³/hr")
    st.write(f"พัดลม: {round(fans)} ตัว")
    st.write(f"Cooling Pad: {pad:.2f} m²")
