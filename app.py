import math
import streamlit as st

st.set_page_config(page_title="KSP Farm Engineering Calculator", page_icon="🐔", layout="centered")
st.title("🐷🐔 KSP Farm Engineering Calculator")
st.caption("Ventilation • Cooling Pad • Pump • L.B. White • Air Inlet • Air Step / Tunnel Door | Preliminary sizing")

tab_vent, tab_heat, tab_inlet, tab_summary = st.tabs(["🌬️ Ventilation / Pad / Pump", "🔥 L.B. White Heater", "🪟 Air Inlet / Air Step / Tunnel Door", "📋 Summary"])

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

    # Shared Cooling Pad dimensions: available to the Air Inlet / Door tab even before clicking Calculate.
    shared_required_cfm = (width_m * 3.28084) * (height_m * 3.28084) * air_speed_fpm
    shared_pad_area = shared_required_cfm * 1.699 / 10000.0
    shared_pad_total_length = shared_pad_area / pad_height
    if layout == "3 ด้าน (ซ้าย-ขวา-หน้า)":
        shared_front = front_length
        shared_side = max(0.0, (shared_pad_total_length - shared_front) / 2)
        shared_layout_valid = shared_front <= shared_pad_total_length
    else:
        shared_front = 0.0
        shared_side = shared_pad_total_length / 2
        shared_layout_valid = True

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
    st.subheader("1️⃣ ขนาดโรงเรือน (เชื่อมโยงจาก Ventilation)")
    h_width, h_length, h_height = width_m, house_length, height_m
    st.info(f"กว้าง {h_width:g} m × ยาว {h_length:g} m × สูง {h_height:g} m — แก้ไขได้ที่แท็บ Ventilation")
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
        [1.66, 1.699],
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

    st.divider()
    st.subheader("4️⃣ Air Step / Tunnel Door (เชื่อมโยงกับ Cooling Pad)")
    st.caption("ความสูงช่องเปิด = ความสูง Cooling Pad × 85% | ความกว้างช่องเปิดแต่ละด้าน = ความยาว Pad ที่ติดตั้งด้านนั้น")
    opening_ratio = st.number_input("สัดส่วนความสูงช่องเปิดเทียบกับ Pad (%)", min_value=1.0, max_value=100.0,
                                    value=85.0, step=1.0, key="opening_ratio")
    opening_height = pad_height * opening_ratio / 100.0
    st.write(f"ความสูง Cooling Pad: **{pad_height:.2f} m** → ความสูง Air Step / Tunnel Door: **{opening_height:.3f} m**")
    st.write(f"รูปแบบติดตั้ง Pad: **{layout}**")
    if not shared_layout_valid:
        st.error("ความยาว Pad ด้านหน้ามากกว่าความยาว Pad รวม กรุณากลับไปปรับที่แท็บ Ventilation")
        opening_sides = []
    elif layout == "3 ด้าน (ซ้าย-ขวา-หน้า)":
        opening_sides = [("ด้านหน้า", shared_front), ("ด้านซ้าย", shared_side), ("ด้านขวา", shared_side)]
    else:
        opening_sides = [("ด้านซ้าย", shared_side), ("ด้านขวา", shared_side)]
        st.info("ปัจจุบัน Cooling Pad เลือกติดตั้ง 2 ด้าน จึงแสดงช่องเปิด 2 ด้าน หากต้องการคำนวณ 3 ด้าน ให้เลือก 3 ด้านในแท็บ Ventilation")
    opening_report_rows = []
    for name, length in opening_sides:
        area = length * opening_height
        st.write(f"**{name}:** กว้าง {length:.2f} m × สูง {opening_height:.3f} m = **{area:.2f} m²**")
        opening_report_rows.append(f"{name}: width {length:.2f} m x height {opening_height:.3f} m = {area:.2f} m2")
    if opening_sides:
        total_opening_area = sum(length * opening_height for _, length in opening_sides)
        st.metric("พื้นที่ช่องเปิดรวม", f"{total_opening_area:,.2f} m²")
        if shared_side > house_length:
            st.warning("ความยาวช่องเปิดด้านข้างเกินความยาวโรงเรือน")
        if shared_front > width_m:
            st.warning("ความยาวช่องเปิดด้านหน้าเกินความกว้างโรงเรือน")
    st.warning("Air Step / Tunnel Door: ค่านี้เป็นขนาดช่องเปิดตามสัดส่วน 85% ที่กำหนด ไม่ใช่การยืนยันความเร็วลม/Pressure Drop ต้องตรวจสอบ free area และความต้านทานของช่องเปิดจริง")

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
        "Air Step / Tunnel Door:",
        f"Cooling Pad height: {pad_height:.2f} m",
        f"Opening height ratio: {opening_ratio:.1f}%",
        f"Opening height: {opening_height:.3f} m",
        f"Pad layout: {layout}",
        *opening_report_rows,
        "Note: preliminary sizing. Verify capacity at operating static pressure and inlet distribution.",
    ])
    st.download_button("📥 ดาวน์โหลดรายงาน Air Inlet (.txt)", data=inlet_report,
                       file_name="KSP_Air_Inlet_Report.txt", mime="text/plain")
    st.warning(
        "จำนวนบานเป็นค่าประมาณจาก CFM ของพัดลมที่ระบุและสัดส่วนที่เลือก "
        "ต้องตรวจสอบความสามารถรับลมของ Air Inlet ที่แรงดันใช้งานจริง "
        "รวมถึงการกระจายตำแหน่งช่องลมและการควบคุม Minimum Ventilation ก่อนติดตั้ง"
    )


# Summary recomputes directly from current widget values, without requiring a button click.
with tab_summary:
    st.header("📋 Summary — Equipment & Design Schedule")
    st.caption("สรุปผลทุกระบบจากค่าที่กรอกล่าสุดโดยอัตโนมัติ (ต่อ 1 โรงเรือน)")

    sum_volume = width_m * house_length * height_m
    sum_area_ft2 = (width_m * 3.28084) * (height_m * 3.28084)
    sum_required_cfm = sum_area_ft2 * air_speed_fpm
    sum_required_m3h = sum_required_cfm * 1.699
    sum_fans = math.ceil(sum_required_cfm / fan_cfm)
    sum_fan_cfm = sum_fans * fan_cfm
    sum_pad_area = sum_required_m3h / 10000.0
    sum_pad_length = sum_pad_area / pad_height
    sum_pad_pieces = math.ceil(sum_pad_area / (pad_height * pad_width))
    sum_pad_sides = ([('ด้านหน้า', front_length), ('ด้านซ้าย', (sum_pad_length-front_length)/2),
                      ('ด้านขวา', (sum_pad_length-front_length)/2)]
                     if layout == '3 ด้าน (ซ้าย-ขวา-หน้า)' else
                     [('ด้านซ้าย', sum_pad_length/2), ('ด้านขวา', sum_pad_length/2)])
    sum_valid = all(length >= 0 for _, length in sum_pad_sides)
    sum_pump_flow = [(name, length * pad_height * (7 / (1.8 * 0.6)) * 1.2)
                     for name, length in sum_pad_sides] if sum_valid else []
    sum_opening_height = pad_height * opening_ratio / 100
    sum_opening_area = sum(sum_opening_height * length for _, length in sum_pad_sides) if sum_valid else 0
    sum_inlet_cfm = sum_fan_cfm * inlet_percent / 100
    sum_inlet_m3h = sum_inlet_cfm * conversion
    sum_inlets = math.ceil(sum_inlet_m3h / inlet_capacity)

    st.subheader("🏠 ข้อมูลโรงเรือน")
    st.write(f"กว้าง **{width_m:,.2f} m** × ยาว **{house_length:,.2f} m** × สูง **{height_m:,.2f} m** | ปริมาตร **{sum_volume:,.2f} m³**")
    st.write(f"Air Speed: **{air_speed_fpm:,.0f} ft/min** | Design Static Pressure: **{design_pressure:.2f} in.w.g.**")

    st.subheader("📦 รายการอุปกรณ์รวมต่อโรงเรือน")
    equipment = [
        {"อุปกรณ์": "Ventilation Fan", "จำนวน": sum_fans, "หน่วย": "ตัว", "รายละเอียด": f"{fan_cfm:,.0f} CFM/ตัว; รวม {sum_fan_cfm:,.0f} CFM"},
        {"อุปกรณ์": "Cooling Pad", "จำนวน": sum_pad_pieces if sum_valid else None, "หน่วย": "ก้อน", "รายละเอียด": f"{pad_height:g} × {pad_width:g} m; พื้นที่รวม {sum_pad_area:,.2f} m²"},
        {"อุปกรณ์": "Water Pump (ตามสูตรเดิม)", "จำนวน": len(sum_pump_flow) if sum_valid else None, "หน่วย": "ตัว", "รายละเอียด": f"อัตราการไหลรวม {sum(flow for _, flow in sum_pump_flow):,.1f} L/min" if sum_valid else "Layout ไม่ถูกต้อง"},
        {"อุปกรณ์": "L.B. White Heater", "จำนวน": heater_count, "หน่วย": "เครื่อง", "รายละเอียด": f"{heater_kw:g} kW/เครื่อง; กำลังรวม {installed_kw:,.1f} kW"},
        {"อุปกรณ์": "Air Inlet", "จำนวน": sum_inlets, "หน่วย": "บาน", "รายละเอียด": f"{inlet_capacity:,.0f} m³/h/บาน; ใช้ลม {inlet_percent:g}%"},
        {"อุปกรณ์": "Air Step / Tunnel Door", "จำนวน": len(sum_pad_sides) if sum_valid else None, "หน่วย": "ด้าน", "รายละเอียด": f"สูง {sum_opening_height:.3f} m; พื้นที่ช่องเปิดรวม {sum_opening_area:,.2f} m²" if sum_valid else "Layout ไม่ถูกต้อง"},
    ]
    st.dataframe(equipment, use_container_width=True, hide_index=True)

    st.subheader("📐 รายละเอียด Cooling Pad / Pump / Tunnel Door แยกตามด้าน")
    if not sum_valid:
        st.error("ความยาว Pad ด้านหน้ามากกว่าความยาว Pad รวม กรุณาปรับข้อมูลในแท็บ Ventilation ก่อนใช้ Summary")
    else:
        detail = []
        for (name, length), (_, flow) in zip(sum_pad_sides, sum_pump_flow):
            detail.append({
                "ตำแหน่ง": name,
                "Pad ยาว (m)": round(length, 2),
                "Pad สูง (m)": pad_height,
                "Pump (L/min)": round(flow, 1),
                "ช่องเปิดกว้าง (m)": round(length, 2),
                "ช่องเปิดสูง (m)": round(sum_opening_height, 3),
                "ช่องเปิด (m²)": round(length * sum_opening_height, 2),
            })
        st.dataframe(detail, use_container_width=True, hide_index=True)
        st.caption("จำนวน Pad เป็นการปัดขึ้นจากพื้นที่รวม ไม่ใช่จำนวนก้อนที่ปัดแยกแต่ละด้าน; จำนวน Pump สมมติ 1 ตัว/ด้าน")

    st.subheader("🔎 ข้อมูลประกอบการคำนวณ")
    st.write(f"Ventilation Required: **{sum_required_cfm:,.0f} CFM** / **{sum_required_m3h:,.0f} m³/h**")
    st.write(f"Cooling Pad: **{sum_pad_area:,.2f} m²** / ความยาวรวม **{sum_pad_length:,.2f} m** / Layout **{layout}**")
    st.write(f"Heater: **{climate}**, Factor **{factor:.3f} kW/m³**, Required **{required_kw:,.1f} kW**, Safety Margin **{safety_margin:g}%**")
    st.write(f"Air Inlet: **{sum_fan_cfm:,.0f} CFM × {inlet_percent:g}% × {conversion:g} = {sum_inlet_m3h:,.0f} m³/h**")
    st.write(f"Air Step / Tunnel Door: Pad สูง **{pad_height:g} m × {opening_ratio:g}% = {sum_opening_height:.3f} m**")

    lines = [
        'KSP FARM ENGINEERING CALCULATOR - SUMMARY',
        f'House (W x L x H): {width_m:g} x {house_length:g} x {height_m:g} m',
        f'House volume: {sum_volume:,.2f} m3',
        f'Air speed: {air_speed_fpm:g} ft/min | Design pressure: {design_pressure:g} in.w.g.',
        f'Airflow required: {sum_required_cfm:,.0f} CFM',
        '', 'EQUIPMENT SCHEDULE',
    ]
    for item in equipment:
        lines.append(f"{item['อุปกรณ์']}: {item['จำนวน']} {item['หน่วย']} | {item['รายละเอียด']}")
    lines.extend(['', 'PAD / PUMP / OPENING BY SIDE'])
    if sum_valid:
        for row in detail:
            lines.append(f"{row['ตำแหน่ง']}: Pad {row['Pad ยาว (m)']} x {row['Pad สูง (m)']} m | Pump {row['Pump (L/min)']} L/min | Opening {row['ช่องเปิดกว้าง (m)']} x {row['ช่องเปิดสูง (m)']} m")
    lines.extend(['', 'ASSUMPTIONS',
                  f'Heating factor: {factor:.3f} kW/m3; margin: {safety_margin:g}%',
                  f'Air inlet fraction: {inlet_percent:g}%; conversion: {conversion:g}; inlet capacity: {inlet_capacity:g} m3/h',
                  'Preliminary calculations only. Verify actual product curves, pressure losses, ventilation, and heat loss.'])
    st.download_button('📥 ดาวน์โหลด Summary (.txt)', '\n'.join(lines),
                       file_name='KSP_Farm_Engineering_Summary.txt', mime='text/plain',
                       disabled=not sum_valid)
    st.warning('Summary เป็นรายการประมาณการเบื้องต้น ไม่ใช่ BOM เพื่อสั่งซื้อหรือแบบติดตั้งที่ผ่านการรับรอง ต้องตรวจสอบสเปกจริงและการปัดจำนวนแยกแต่ละด้านก่อนใช้งาน')
