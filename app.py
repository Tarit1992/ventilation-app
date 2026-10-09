import math
import streamlit as st

st.set_page_config(page_title="KSP Farm Engineering Calculator", page_icon="🐔", layout="centered")
st.title("🐷🐔 KSP Farm Engineering Calculator")
st.caption("Ventilation • Cooling Pad • Pump • L.B. White • Air Inlet | Preliminary sizing")

tab_vent, tab_heat, tab_inlet = st.tabs(["🌬️ Ventilation / Pad / Pump", "🔥 L.B. White Heater", "🪟 Air Inlet"])

with tab_vent:
    st.header("1️⃣ ข้อมูลโรงเรือน")
    width_m = st.number_input("ความกว้าง (m)", min_value=0.01, value=18.0, key="v_width")
    height_m = st.number_input("ความสูง (m)", min_value=0.01, value=3.0, key="v_height")
    house_length = st.number_input("ความยาวโรงเรือน (m)", min_value=0.01, value=100.0, key="v_length")
    air_speed_fpm = st.number_input("Air Speed (ft/min)", min_value=0.0, value=800.0)

    st.header("📉 Static Pressure")
    design_pressure = st.selectbox("เลือกแรงดัน (in.w.g.)", [0.15, 0.20, 0.25, 0.30])

    st.header("2️⃣ พัดลม")
    fan_cfm = st.number_input("กำลังพัดลมต่อ 1 ตัว (CFM)", min_value=0.01, value=25000.0)

    st.header("3️⃣ Cooling Pad")
    pad_height = st.selectbox("ความสูง Pad (m)", [1.5, 1.8, 2.0, 2.4])
    pad_width = st.selectbox("ความกว้าง Pad (m)", [0.6, 0.3])
    layout = st.radio("รูปแบบติดตั้ง Pad", ["2 ด้าน (ซ้าย-ขวา)", "3 ด้าน (ซ้าย-ขวา-หน้า)"])
    front_length = 0.0
    if layout == "3 ด้าน (ซ้าย-ขวา-หน้า)":
        front_length = st.number_input("ความยาว Pad ด้านหน้า (m)", min_value=0.0, value=10.0)

    if st.button("คำนวณทั้งหมด", type="primary", key="calculate_vent"):
        width_ft = width_m * 3.28084
        height_ft = height_m * 3.28084
        area_ft2 = width_ft * height_ft
        required_cfm = area_ft2 * air_speed_fpm
        m3hr = required_cfm * 1.699
        num_fans = math.ceil(required_cfm / fan_cfm)
        total_fan_cfm = num_fans * fan_cfm
        extra = total_fan_cfm - required_cfm
        velocity_pressure = (air_speed_fpm / 4005) ** 2
        estimated_static = velocity_pressure + 0.08
        diff = estimated_static - design_pressure
        pad_area = m3hr / 10000
        total_pad_length = pad_area / pad_height

        st.header("📊 ผลลัพธ์")
        st.subheader("🌬️ ความต้องการลม")
        st.write(f"พื้นที่หน้าตัด: {area_ft2:,.0f} ft²")
        st.write(f"ต้องการลม: {required_cfm:,.0f} CFM")
        st.write(f"≈ {m3hr:,.0f} m³/hr")

        st.subheader("🌀 พัดลม")
        st.write(f"จำนวนพัดลม: {num_fans} ตัว")
        st.write(f"ลมรวมจากพัดลม: {total_fan_cfm:,.0f} CFM")
        st.write(f"ส่วนเกิน/ขาด: {extra:,.0f} CFM")
        if total_fan_cfm >= required_cfm:
            st.success("✔ พัดลมเพียงพอตามค่า CFM ที่ป้อน")
        else:
            st.error("❌ พัดลมไม่พอ")

        st.subheader("📉 ตรวจสอบแรงดัน")
        st.write(f"Velocity Pressure: {velocity_pressure:.3f} in.w.g.")
        st.write(f"Estimated Static: {estimated_static:.3f} in.w.g.")
        st.write(f"Design Pressure: {design_pressure:.2f} in.w.g.")
        if abs(diff) < 0.03:
            st.success("✔ ค่าแรงดันใกล้เคียงค่าที่กำหนด (ตามสูตรเดิม)")
        elif diff < 0:
            st.warning("⚠️ ค่าแรงดันประมาณต่ำกว่าค่าที่กำหนด")
        else:
            st.error("❌ ค่าแรงดันประมาณสูงกว่าค่าที่กำหนด")
        st.caption("สูตร Static Pressure นี้เป็นสูตรประมาณเดิม ไม่ใช่การคำนวณความสูญเสียแรงดันของระบบทั้งหมด")

        st.subheader("🧊 Cooling Pad")
        st.write(f"พื้นที่ Pad: {pad_area:.2f} m²")
        st.write(f"ความยาว Pad รวม: {total_pad_length:.2f} m")
        if layout == "2 ด้าน (ซ้าย-ขวา)":
            side_length = total_pad_length / 2
            if side_length > house_length:
                st.warning("⚠️ Pad ยาวเกินโรงเรือน")
            side_lengths = [side_length, side_length]
            st.write(f"ซ้าย/ขวา: {side_length:.2f} m")
        else:
            remaining = total_pad_length - front_length
            if remaining < 0:
                st.error("❌ ความยาวด้านหน้ามากกว่าความยาว Pad รวมที่คำนวณได้")
                side_lengths = []
            else:
                side_length = remaining / 2
                st.write(f"ด้านหน้า: {front_length:.2f} m")
                st.write(f"ซ้าย/ขวา: {side_length:.2f} m")
                side_lengths = [side_length, side_length, front_length]
                if side_length > house_length:
                    st.warning("⚠️ Pad ด้านข้างยาวเกินโรงเรือน")
                if front_length > width_m:
                    st.warning("⚠️ Pad ด้านหน้ายาวเกินความกว้างโรงเรือน")
        if side_lengths:
            pad_per_piece = pad_height * pad_width
            num_pads = math.ceil(pad_area / pad_per_piece)
            st.write(f"จำนวนก้อน Pad ตามพื้นที่รวม: {num_pads} ก้อน")
            st.caption("จำนวนก้อนตามพื้นที่รวมอาจต่างจากจำนวนจริงเมื่อปัดจำนวนก้อนแยกตามแต่ละด้าน")
            st.subheader("💧 Pump")
            base_area = 1.8 * 0.6
            flow_per_m2 = 7 / base_area
            pumps = []
            for i, length in enumerate(side_lengths):
                area_side = length * pad_height
                flow_safe = area_side * flow_per_m2 * 1.2
                pumps.append(flow_safe)
                st.write(f"ด้านที่ {i + 1}: {flow_safe:,.0f} L/min")
            st.write(f"จำนวนปั๊มตามสูตรเดิม: {len(pumps)} ตัว")
            st.write(f"ปั๊มรวมทั้งหมด: {sum(pumps):,.0f} L/min")
            st.caption("จำนวนปั๊มและอัตราน้ำเป็นค่าประมาณตามสูตรเดิม ต้องตรวจสอบสเปก Pad และ Pump จริง")

with tab_heat:
    st.header("🔥 L.B. White Heater Calculator")
    st.caption("คำนวณกำลังความร้อนเบื้องต้นด้วย Heating Factor จากสไลด์ KSP")
    st.subheader("1️⃣ ขนาดโรงเรือน")
    col1, col2, col3 = st.columns(3)
    with col1:
        h_width = st.number_input("กว้าง (m)", min_value=0.01, value=10.0, key="h_width")
    with col2:
        h_length = st.number_input("ยาว (m)", min_value=0.01, value=60.0, key="h_length")
    with col3:
        h_height = st.number_input("สูงเฉลี่ย (m)", min_value=0.01, value=2.4, key="h_height")
    volume = h_width * h_length * h_height
    st.metric("ปริมาตรโรงเรือน", f"{volume:,.1f} m³")

    st.subheader("2️⃣ Climate & Temperature")
    c1, c2 = st.columns(2)
    with c1:
        outdoor_temp = st.number_input("อุณหภูมิภายนอก (°C)", value=0.0, step=1.0)
    with c2:
        indoor_temp = st.number_input("อุณหภูมิภายในเป้าหมาย (°C)", value=33.0, step=1.0)
    climate = st.selectbox("Heating Factor", ["Tropical (0.050 kW/m³)", "Temperate (0.075 kW/m³)", "Cold (0.100 kW/m³)", "Custom"], index=2)
    factors = {"Tropical (0.050 kW/m³)": 0.05, "Temperate (0.075 kW/m³)": 0.075, "Cold (0.100 kW/m³)": 0.10}
    if climate == "Custom":
        factor = st.number_input("Custom Factor (kW/m³)", min_value=0.001, value=0.1, step=0.005, format="%.3f")
    else:
        factor = factors[climate]
    st.info("อุณหภูมิภายนอกและภายในใช้แสดงเงื่อนไขออกแบบเท่านั้น สูตร Heating Factor ไม่ได้คำนวณ Heat Loss จากผลต่างอุณหภูมิโดยตรง")

    st.subheader("3️⃣ Heater Model")
    heater_model = st.selectbox("รุ่นเครื่อง", ["L.B. White AD250 (73 kW)", "Custom capacity"])
    if heater_model == "L.B. White AD250 (73 kW)":
        heater_kw = 73.0
        st.write("กำลังความร้อนต่อเครื่อง: **73 kW** (ตามสไลด์ KSP)")
    else:
        heater_kw = st.number_input("กำลัง Heater ต่อเครื่อง (kW)", min_value=0.01, value=73.0, step=1.0)
    safety_margin = st.number_input("Safety Margin (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0)

    base_kw = volume * factor
    required_kw = base_kw * (1 + safety_margin / 100)
    heater_count = math.ceil(required_kw / heater_kw)
    installed_kw = heater_count * heater_kw

    st.subheader("4️⃣ ผลการคำนวณ")
    st.metric("จำนวน Heater ที่ต้องการ", f"{heater_count:,} เครื่อง")
    r1, r2, r3 = st.columns(3)
    r1.metric("Required", f"{required_kw:,.1f} kW")
    r2.metric("Installed", f"{installed_kw:,.1f} kW")
    r3.metric("Reserve", f"{installed_kw-required_kw:,.1f} kW")
    st.write(f"สูตร: {volume:,.1f} m³ × {factor:.3f} kW/m³ × (1 + {safety_margin:.0f}%) ÷ {heater_kw:,.1f} kW/เครื่อง")
    st.write(f"อุณหภูมิภายนอก {outdoor_temp:g}°C | อุณหภูมิเป้าหมาย {indoor_temp:g}°C | ΔT = {indoor_temp-outdoor_temp:g}°C")
    report = "\n".join([
        "KSP - L.B. White Heater Calculation",
        f"House: {h_width:g} x {h_length:g} x {h_height:g} m",
        f"Volume: {volume:,.1f} m3",
        f"Outdoor temperature: {outdoor_temp:g} C",
        f"Indoor target temperature: {indoor_temp:g} C",
        f"Climate: {climate}",
        f"Factor: {factor:.3f} kW/m3",
        f"Safety margin: {safety_margin:g}%",
        f"Base heating requirement: {base_kw:,.1f} kW",
        f"Required heating: {required_kw:,.1f} kW",
        f"Heater: {heater_model}, {heater_kw:g} kW/unit",
        f"Required units: {heater_count}",
        f"Installed heating capacity: {installed_kw:,.1f} kW",
        "Note: preliminary factor-based estimate; engineering heat-loss verification required.",
    ])
    st.download_button("📥 ดาวน์โหลดผลคำนวณ (.txt)", data=report, file_name="KSP_LB_White_Heater_Report.txt", mime="text/plain")
    st.warning("ผลคำนวณเป็น Preliminary Sizing เท่านั้น ค่า Factor จากสไลด์ไม่ได้รับรองสำหรับทุกภูมิอากาศ ต้องตรวจสอบ Heat Loss ผ่านหลังคา/ผนัง การระบายอากาศ ประสิทธิภาพ Heater และคู่มือผู้ผลิตก่อนเลือกจำนวนเครื่องจริง")


with tab_inlet:
    st.header("🪟 Air Inlet Calculator")
    st.caption("ใช้กำลังลมรวมของพัดลมจากแท็บ Ventilation โดยคำนวณจากค่าที่กรอกล่าสุดอัตโนมัติ")

    inlet_area_ft2 = (width_m * 3.28084) * (height_m * 3.28084)
    inlet_required_cfm = inlet_area_ft2 * air_speed_fpm
    inlet_fan_count = math.ceil(inlet_required_cfm / fan_cfm)
    inlet_total_fan_cfm = inlet_fan_count * fan_cfm

    st.subheader("1️⃣ กำลังลมจากพัดลม")
    a, b = st.columns(2)
    a.metric("จำนวนพัดลม", f"{inlet_fan_count:,} ตัว")
    b.metric("CFM รวมจากพัดลม", f"{inlet_total_fan_cfm:,.0f} CFM")
    st.caption("หากต้องการเปลี่ยน CFM หรือจำนวนพัดลม ให้กลับไปแก้ค่าที่แท็บ Ventilation")

    st.subheader("2️⃣ กำหนดสัดส่วนลมผ่าน Air Inlet")
    inlet_percent = st.number_input(
        "สัดส่วนลมที่ผ่าน Air Inlet (%)", min_value=0.0, max_value=100.0,
        value=50.0, step=5.0, key="inlet_percent",
    )
    conversion = st.selectbox(
        "ตัวคูณแปลง CFM เป็น m³/h",
        [1.699, 1.699],
        format_func=lambda v: "1.66 (ตามสูตร KSP ที่ระบุ)" if v == 1.66 else "1.699 (ค่าการแปลงหน่วยมาตรฐานโดยประมาณ)",
        key="inlet_conversion",
    )
    inlet_capacity = st.number_input(
        "ปริมาณลมผ่าน Air Inlet ต่อ 1 บาน (m³/h)",
        min_value=0.01, value=1800.0, step=100.0, key="inlet_capacity",
    )

    inlet_cfm = inlet_total_fan_cfm * inlet_percent / 100.0
    inlet_m3h = inlet_cfm * conversion
    inlet_count = math.ceil(inlet_m3h / inlet_capacity)
    inlet_installed_m3h = inlet_count * inlet_capacity

    st.subheader("3️⃣ ผลการคำนวณ Air Inlet")
    st.metric("จำนวน Air Inlet ที่ต้องการ", f"{inlet_count:,} บาน / โรงเรือน")
    x, y, z = st.columns(3)
    x.metric("ลมผ่าน Inlet", f"{inlet_cfm:,.0f} CFM")
    y.metric("แปลงหน่วย", f"{inlet_m3h:,.0f} m³/h")
    z.metric("กำลังรับลมรวม", f"{inlet_installed_m3h:,.0f} m³/h")
    st.write(f"CFM จากพัดลม = {inlet_fan_count:,} × {fan_cfm:,.0f} = **{inlet_total_fan_cfm:,.0f} CFM**")
    st.write(f"ลมผ่าน Air Inlet = {inlet_total_fan_cfm:,.0f} × {inlet_percent:g}% = **{inlet_cfm:,.0f} CFM**")
    st.write(f"แปลงเป็น m³/h = {inlet_cfm:,.0f} × {conversion:g} = **{inlet_m3h:,.0f} m³/h**")
    st.write(f"จำนวนบาน = ปัดขึ้น({inlet_m3h:,.0f} ÷ {inlet_capacity:,.0f}) = **{inlet_count:,} บาน**")

    inlet_report = "\n".join([
        "KSP - Air Inlet Calculation",
        f"House: {width_m:g} x {house_length:g} x {height_m:g} m",
        f"Air speed: {air_speed_fpm:g} ft/min",
        f"Fan quantity: {inlet_fan_count}",
        f"Fan CFM per unit: {fan_cfm:,.2f}",
        f"Total fan airflow: {inlet_total_fan_cfm:,.2f} CFM",
        f"Inlet airflow fraction: {inlet_percent:g}%",
        f"Airflow through inlets: {inlet_cfm:,.2f} CFM",
        f"CFM to m3/h factor: {conversion:g}",
        f"Inlet airflow: {inlet_m3h:,.2f} m3/h",
        f"Inlet capacity per unit: {inlet_capacity:,.2f} m3/h",
        f"Required air inlets: {inlet_count} units",
        "Note: preliminary sizing. Verify capacity at operating static pressure and inlet distribution.",
    ])
    st.download_button("📥 ดาวน์โหลดรายงาน Air Inlet (.txt)", data=inlet_report,
                       file_name="KSP_Air_Inlet_Report.txt", mime="text/plain")
    st.warning(
        "จำนวนบานเป็นค่าประมาณจาก CFM ของพัดลมที่ระบุและสัดส่วนที่เลือก "
        "ต้องตรวจสอบความสามารถรับลมของ Air Inlet ที่แรงดันใช้งานจริง "
        "รวมถึงการกระจายตำแหน่งช่องลมและการควบคุม Minimum Ventilation ก่อนติดตั้ง"
    )
