import math
import io
import streamlit as st

def calculate_pad_layout(total_fan_cfm, pad_height, pad_width, layout, requested_front_m, face_velocity_fpm):
    """Allocate whole pad modules, keeping left and right exactly balanced."""
    area_ft2 = total_fan_cfm / face_velocity_fpm
    area_m2 = area_ft2 / 10.764
    theoretical_modules = area_m2 / (pad_height * pad_width)
    minimum_modules = math.ceil(theoretical_modules - 1e-10)
    if layout.startswith("3 ด้าน"):
        front_modules = math.ceil(requested_front_m / pad_width - 1e-10)
    else:
        front_modules = 0
    # Both side walls have the same number of whole modules. This can
    # increase the installed count above the theoretical minimum.
    side_modules = max(0, math.ceil((minimum_modules - front_modules) / 2))
    sides = ([('ด้านหน้า', front_modules)] if layout.startswith('3 ด้าน') else []) + [
        ('ด้านซ้าย', side_modules), ('ด้านขวา', side_modules)
    ]
    actual_modules = sum(qty for _, qty in sides)
    return dict(area_ft2=area_ft2, area_m2=area_m2,
                theoretical_modules=theoretical_modules, minimum_modules=minimum_modules,
                sides=sides, actual_modules=actual_modules,
                actual_area_m2=actual_modules * pad_height * pad_width,
                actual_length_m=actual_modules * pad_width)


# Product catalogue transcribed from supplied MULTI LAYER LARGE table (millimetres).
# Verify manufacturer drawings before procurement, especially the 5-layer row.
AIR_STEP_MODELS = [
    {"layers": 1, "external_mm": 489, "installation_mm": 389, "opening_mm": 404},
    {"layers": 2, "external_mm": 868, "installation_mm": 768, "opening_mm": 783},
    {"layers": 3, "external_mm": 1247, "installation_mm": 1147, "opening_mm": 1162},
    {"layers": 4, "external_mm": 1626, "installation_mm": 1526, "opening_mm": 1541},
    {"layers": 5, "external_mm": 2005, "installation_mm": 1950, "opening_mm": 1920},
    {"layers": 6, "external_mm": 2384, "installation_mm": 2284, "opening_mm": 2299},
]

def select_air_step(pad_height_m, target_ratio):
    """Closest external height to target, but never taller than Cooling Pad."""
    limit_mm = pad_height_m * 1000
    target_mm = limit_mm * target_ratio / 100
    eligible = [m for m in AIR_STEP_MODELS if m["external_mm"] <= limit_mm + 1e-8]
    if not eligible:
        return None
    return min(eligible, key=lambda m: (abs(m["external_mm"] - target_mm), -m["external_mm"]))

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
    pad_face_velocity = st.number_input("ความเร็วลมหน้าเยื่อ (ft/min)", min_value=1.0, value=300.0, step=10.0, key="pad_face_velocity")
    layout = st.radio("รูปแบบติดตั้ง Pad", ["2 ด้าน (ซ้าย-ขวา)", "3 ด้าน (ซ้าย-ขวา-หน้า)"])
    front_length = 0.0
    if layout == "3 ด้าน (ซ้าย-ขวา-หน้า)":
        auto_front = st.checkbox("ใช้ความกว้างโรงเรือนเป็นความยาว Pad ด้านหน้าอัตโนมัติ", value=True)
        if auto_front:
            front_length = width_m
            st.info(f"ความยาว Pad ด้านหน้าอ้างอิงความกว้างโรงเรือน = {front_length:,.2f} m (จำนวนก้อนปัดขึ้นตามขนาดจริง)")
        else:
            front_length = st.number_input("ความยาว Pad ด้านหน้า (m)", min_value=0.0, value=float(width_m))

    # Single source of truth for Pad, Pump, Door and Summary.
    shared_required_cfm = (width_m * 3.28084) * (height_m * 3.28084) * air_speed_fpm
    shared_fan_count = math.ceil(shared_required_cfm / fan_cfm)
    shared_total_fan_cfm = shared_fan_count * fan_cfm
    pad_design = calculate_pad_layout(shared_total_fan_cfm, pad_height, pad_width,
                                      layout, front_length, pad_face_velocity)
    pad_sides = [(name, qty, qty * pad_width) for name, qty in pad_design['sides']]
    shared_pad_area = pad_design['actual_area_m2']
    shared_pad_total_length = pad_design['actual_length_m']
    shared_front = next((length for name, qty, length in pad_sides if name == 'ด้านหน้า'), 0.0)
    shared_side = next((length for name, qty, length in pad_sides if name == 'ด้านซ้าย'), 0.0)
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
        pad_area = pad_design['area_m2']
        total_pad_length = pad_design['actual_length_m']

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
        st.write(f"CFM รวมพัดลม: **{total_fan_cfm:,.0f} CFM**")
        st.write(f"พื้นที่เยื่อที่ต้องการ = {total_fan_cfm:,.0f} ÷ {pad_face_velocity:g} ÷ 10.764 = **{pad_area:,.2f} m²**")
        st.write(f"ขนาดเยื่อ: **{pad_height:g} × {pad_width:g} m**")
        st.write(f"จำนวนก้อนขั้นต่ำตามพื้นที่ = ปัดขึ้น({pad_area:,.2f} ÷ {pad_height*pad_width:.3f}) = **{pad_design['minimum_modules']:,} ก้อน**")
        st.metric("จำนวนก้อนติดตั้งจริง (สมดุลซ้าย/ขวา)", f"{pad_design['actual_modules']:,} ก้อน")
        st.write(f"พื้นที่เยื่อติดตั้งจริง: **{pad_design['actual_area_m2']:,.2f} m²** | ความยาวรวม: **{total_pad_length:,.2f} m**")
        for name, qty, length in pad_sides:
            st.write(f"{name}: **{qty:,} ก้อน × {pad_width:g} m = {length:,.2f} m**")
        if shared_side > house_length:
            st.warning("⚠️ ความยาวเยื่อด้านข้างเกินความยาวโรงเรือน")
        if shared_front > width_m:
            st.warning("⚠️ ความยาวเยื่อด้านหน้าเกินความกว้างโรงเรือน")
        st.caption("ด้านหน้าปัดขึ้นตามจำนวนก้อนเต็มก่อน แล้วแบ่งก้อนที่เหลือให้ซ้ายและขวาเท่ากัน; อาจมีจำนวนก้อนติดตั้งจริงมากกว่าขั้นต่ำ")
        st.subheader("💧 Pump")
        flow_per_m2 = 7 / (1.8 * 0.6)
        pumps = []
        for name, qty, length in pad_sides:
            if qty == 0:
                continue
            flow_safe = length * pad_height * flow_per_m2 * 1.2
            pumps.append(flow_safe)
            st.write(f"{name}: **{flow_safe:,.1f} L/min**")
        st.write(f"จำนวนปั๊มตามสมมติฐาน 1 ตัว/ด้านที่มีเยื่อ: **{len(pumps)} ตัว**")
        st.write(f"ปั๊มรวมทั้งหมด: **{sum(pumps):,.1f} L/min**")
        st.caption("ปริมาณน้ำและจำนวนปั๊มตามสมมติฐานเดิม ต้องตรวจสอบคู่มือเยื่อและ Pump จริง")

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
    target_height = pad_height * opening_ratio / 100.0
    chosen_step = select_air_step(pad_height, opening_ratio)
    st.write(f"ความสูงเป้าหมาย: **{target_height:.3f} m** ({opening_ratio:g}% ของ Pad {pad_height:g} m)")
    st.caption("เลือกรุ่นที่ความสูงภายนอกใกล้ค่าเป้าหมายที่สุด และต้องไม่สูงกว่า Cooling Pad")
    st.dataframe([{
        "Layers": m["layers"], "External (mm)": m["external_mm"],
        "Installation (mm)": m["installation_mm"], "Opening (mm)": m["opening_mm"]
    } for m in AIR_STEP_MODELS], hide_index=True, use_container_width=True)
    opening_sides = [(name, length) for name, qty, length in pad_sides if qty > 0]
    opening_report_rows = []
    if chosen_step is None:
        opening_height = 0.0
        st.error("ไม่มีรุ่น Air Step ที่ความสูงภายนอกไม่เกินความสูง Pad")
    else:
        opening_height = chosen_step["external_mm"] / 1000
        st.success(f"แนะนำ Air Step **{chosen_step['layers']} Layers** | External {opening_height:.3f} m | Installation {chosen_step['installation_mm']/1000:.3f} m | Opening {chosen_step['opening_mm']/1000:.3f} m")
        st.write(f"รูปแบบติดตั้ง Pad: **{layout}**")
        if layout.startswith('2 ด้าน'):
            st.info("ติดตั้งเยื่อ 2 ด้าน หากต้องการช่องเปิด 3 ด้านให้เปลี่ยน Layout ในแท็บ Ventilation")
        for name, length in opening_sides:
            area = length * opening_height
            st.write(f"**{name}:** ยาว {length:.2f} m × สูงภายนอก {opening_height:.3f} m = **{area:.2f} m²** | {chosen_step['layers']} Layers")
            opening_report_rows.append(f"{name}: {length:.2f} m length x {opening_height:.3f} m external height; {chosen_step['layers']} layers; installation height {chosen_step['installation_mm']/1000:.3f} m; opening height {chosen_step['opening_mm']/1000:.3f} m")
        if opening_sides:
            st.metric("พื้นที่กรอบภายนอกรวม (ไม่ใช่ Free Area)", f"{sum(length * opening_height for _, length in opening_sides):,.2f} m²")
            if shared_side > house_length:
                st.warning("ความยาวช่องเปิดด้านข้างเกินความยาวโรงเรือน")
            if shared_front > width_m:
                st.warning("ความยาวช่องเปิดด้านหน้าเกินความกว้างโรงเรือน")
    st.warning("ขนาดในแค็ตตาล็อกเป็นความสูงของสินค้า ไม่ใช่พื้นที่เปิดสุทธิ; ต้องตรวจสอบแบบติดตั้ง, แรงดันตกคร่อม และสเปกจริงก่อนสั่งซื้อ โดยเฉพาะข้อมูลรุ่น 5 Layers")

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
        f"Selected Air Step layers: {chosen_step['layers'] if chosen_step else 'N/A'}",
        f"External height: {opening_height:.3f} m",
        f"Installation height: {chosen_step['installation_mm']/1000:.3f} m" if chosen_step else "Installation height: N/A",
        f"Opening height: {chosen_step['opening_mm']/1000:.3f} m" if chosen_step else "Opening height: N/A",
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
    sum_pad_area = pad_design['area_m2']
    sum_pad_length = pad_design['actual_length_m']
    sum_pad_pieces = pad_design['actual_modules']
    sum_pad_sides = [(name, length) for name, qty, length in pad_sides if qty > 0]
    sum_valid = True
    sum_pump_flow = [(name, length * pad_height * (7 / (1.8 * 0.6)) * 1.2)
                     for name, length in sum_pad_sides]
    sum_step = select_air_step(pad_height, opening_ratio)
    sum_opening_height = sum_step["external_mm"] / 1000 if sum_step else 0.0
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
        {"อุปกรณ์": "Cooling Pad", "จำนวน": sum_pad_pieces if sum_valid else None, "หน่วย": "ก้อน", "รายละเอียด": f"{pad_height:g} × {pad_width:g} m; พื้นที่ติดตั้ง {pad_design['actual_area_m2']:,.2f} m²"},
        {"อุปกรณ์": "Water Pump (ตามสูตรเดิม)", "จำนวน": len(sum_pump_flow) if sum_valid else None, "หน่วย": "ตัว", "รายละเอียด": f"อัตราการไหลรวม {sum(flow for _, flow in sum_pump_flow):,.1f} L/min" if sum_valid else "Layout ไม่ถูกต้อง"},
        {"อุปกรณ์": "L.B. White Heater", "จำนวน": heater_count, "หน่วย": "เครื่อง", "รายละเอียด": f"{heater_kw:g} kW/เครื่อง; กำลังรวม {installed_kw:,.1f} kW"},
        {"อุปกรณ์": "Air Inlet", "จำนวน": sum_inlets, "หน่วย": "บาน", "รายละเอียด": f"{inlet_capacity:,.0f} m³/h/บาน; ใช้ลม {inlet_percent:g}%"},
        {"อุปกรณ์": "Air Step / Tunnel Door", "จำนวน": len(sum_pad_sides) if sum_valid else None, "หน่วย": "ด้าน", "รายละเอียด": f"{sum_step['layers']} Layers; สูงภายนอก {sum_opening_height:.3f} m; ยาวรวม {sum_pad_length:.2f} m" if sum_step else "ไม่มีรุ่นที่เหมาะสม" if sum_valid else "Layout ไม่ถูกต้อง"},
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
                "Pad (ก้อน)": round(length / pad_width),
                "Pad ยาว (m)": round(length, 2),
                "Pad สูง (m)": pad_height,
                "Pump (L/min)": round(flow, 1),
                "ช่องเปิดกว้าง (m)": round(length, 2),
                "Air Step Layers": sum_step["layers"] if sum_step else "N/A",
                "Air Step สูงภายนอก (m)": round(sum_opening_height, 3),
                "Air Step สูงติดตั้ง (m)": round(sum_step["installation_mm"]/1000, 3) if sum_step else None,
                "Air Step Opening (m)": round(sum_step["opening_mm"]/1000, 3) if sum_step else None,
                "ช่องเปิดสูง (m)": round(sum_opening_height, 3),
                "ช่องเปิด (m²)": round(length * sum_opening_height, 2),
            })
        st.dataframe(detail, use_container_width=True, hide_index=True)
        st.caption("จำนวน Pad คำนวณจาก CFM รวมของพัดลม / ความเร็วหน้าเยื่อ / 10.764 และปัดเป็นก้อนเต็มให้ซ้าย/ขวาเท่ากัน; Pump สมมติ 1 ตัว/ด้าน")

    st.subheader("🔎 ข้อมูลประกอบการคำนวณ")
    st.write(f"Ventilation Required: **{sum_required_cfm:,.0f} CFM** / **{sum_required_m3h:,.0f} m³/h**")
    st.write(f"Cooling Pad: CFM พัดลม **{sum_fan_cfm:,.0f}** ÷ {pad_face_velocity:g} ÷ 10.764 = **{sum_pad_area:,.2f} m²**; ติดตั้ง **{sum_pad_pieces} ก้อน**, ยาวรวม **{sum_pad_length:,.2f} m** / Layout **{layout}**")
    st.write(f"Heater: **{climate}**, Factor **{factor:.3f} kW/m³**, Required **{required_kw:,.1f} kW**, Safety Margin **{safety_margin:g}%**")
    st.write(f"Air Inlet: **{sum_fan_cfm:,.0f} CFM × {inlet_percent:g}% × {conversion:g} = {sum_inlet_m3h:,.0f} m³/h**")
    st.write(f"Air Step / Tunnel Door: ความสูงเป้าหมาย **{pad_height * opening_ratio/100:.3f} m** → รุ่น **{sum_step['layers']} Layers** สูงภายนอก **{sum_opening_height:.3f} m**" if sum_step else "ไม่มีรุ่น Air Step ที่ไม่สูงกว่า Pad")

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
            lines.append(f"{row['ตำแหน่ง']}: Pad {row['Pad ยาว (m)']} x {row['Pad สูง (m)']} m | Pump {row['Pump (L/min)']} L/min | Air Step {row['Air Step Layers']} layers, length {row['ช่องเปิดกว้าง (m)']} m x external height {row['ช่องเปิดสูง (m)']} m; installation height {row['Air Step สูงติดตั้ง (m)']} m; opening height {row['Air Step Opening (m)']} m")
    lines.extend(['', 'ASSUMPTIONS',
                  f'Heating factor: {factor:.3f} kW/m3; margin: {safety_margin:g}%',
                  f'Air inlet fraction: {inlet_percent:g}%; conversion: {conversion:g}; inlet capacity: {inlet_capacity:g} m3/h',
                  'Preliminary calculations only. Verify actual product curves, pressure losses, ventilation, and heat loss.'])
    # Exports reproduce the same four sections and tables shown on the Summary tab.
    # English-only exports avoid server-side Thai font dependencies.
    house_rows = [
        ("House width (m)", f"{width_m:,.2f}"),
        ("House length (m)", f"{house_length:,.2f}"),
        ("House height (m)", f"{height_m:,.2f}"),
        ("House volume (m3)", f"{sum_volume:,.2f}"),
        ("Air speed (ft/min)", f"{air_speed_fpm:,.0f}"),
        ("Design static pressure (in.w.g.)", f"{design_pressure:.2f}"),
    ]
    export_equipment = [
        ["Ventilation Fan", sum_fans, "units", f"{fan_cfm:,.0f} CFM/unit; installed {sum_fan_cfm:,.0f} CFM"],
        ["Cooling Pad", sum_pad_pieces, "pieces", f"{pad_height:g} x {pad_width:g} m; installed area {pad_design['actual_area_m2']:,.2f} m2"],
        ["Water Pump (estimated)", len(sum_pump_flow), "units", f"Total design flow {sum(flow for _, flow in sum_pump_flow):,.1f} L/min"],
        ["L.B. White Heater", heater_count, "units", f"{heater_kw:g} kW/unit; installed {installed_kw:,.1f} kW"],
        ["Air Inlet", sum_inlets, "units", f"{inlet_capacity:,.0f} m3/h/unit; airflow share {inlet_percent:g}%"],
        ["Air Step / Tunnel Door", len(sum_pad_sides), "sides", f"{sum_step['layers']} layers; external height {sum_opening_height:.3f} m; total length {sum_pad_length:.2f} m" if sum_step else "No suitable layer model"],
    ]
    export_detail = []
    for (side, length), (_, flow) in zip(sum_pad_sides, sum_pump_flow):
        side_label = {"ด้านหน้า":"Front", "ด้านซ้าย":"Left", "ด้านขวา":"Right", "ซ้าย":"Left", "ขวา":"Right"}.get(side, side)
        export_detail.append([
            side_label, round(length / pad_width), round(length, 2), pad_height,
            round(flow, 1), sum_step['layers'] if sum_step else "N/A",
            round(sum_opening_height, 3),
            round(sum_step['installation_mm']/1000, 3) if sum_step else "N/A",
            round(sum_step['opening_mm']/1000, 3) if sum_step else "N/A",
            round(length * sum_opening_height, 2),
        ])
    export_detail_headers = ["Side", "Pad pcs", "Pad length (m)", "Pad height (m)",
                             "Pump (L/min)", "Air Step layers", "External height (m)",
                             "Install height (m)", "Opening height (m)", "Opening area (m2)"]
    calc_rows = [
        ("Ventilation Required", f"{sum_required_cfm:,.0f} CFM / {sum_required_m3h:,.0f} m3/h"),
        ("Cooling Pad", f"{sum_fan_cfm:,.0f} CFM / {pad_face_velocity:g} / 10.764 = {sum_pad_area:,.2f} m2; {sum_pad_pieces} pieces; total length {sum_pad_length:,.2f} m"),
        ("Heater", f"{climate}; factor {factor:.3f} kW/m3; required {required_kw:,.1f} kW; margin {safety_margin:g}%"),
        ("Air Inlet", f"{sum_fan_cfm:,.0f} CFM x {inlet_percent:g}% x {conversion:g} = {sum_inlet_m3h:,.0f} m3/h"),
        ("Air Step / Tunnel Door", f"{sum_step['layers']} layers; external height {sum_opening_height:.3f} m; target {pad_height*opening_ratio/100:.3f} m" if sum_step else "No suitable model"),
    ]
    from PIL import Image, ImageDraw, ImageFont
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    def export_font(size):
        # Pillow ships DejaVu Sans in most environments; fallback is always available.
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()

    def make_jpg():
        font_title = export_font(39)
        font_head = export_font(26)
        font_body = export_font(20)
        font_small = export_font(17)
        width, margin = 1754, 70  # A4 landscape-like ratio, high-resolution JPG
        navy, red, pale, gray = "#183153", "#C62828", "#EEF2F7", "#475569"
        sections = [
            ("01  HOUSE DIMENSIONS", ["Parameter", "Value"], house_rows),
            ("02  EQUIPMENT SCHEDULE", ["Equipment", "Qty", "Unit", "Specification"], export_equipment),
        ]
        if export_detail:
            sections.append(("03  PAD / PUMP / AIR STEP BY SIDE", export_detail_headers, export_detail))
        sections.append(("04  CALCULATION DETAILS", ["Parameter", "Details"], calc_rows))
        image = Image.new("RGB", (width, 6000), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, 105), fill=navy)
        draw.text((margin, 24), "KSP  |  FARM ENGINEERING SUMMARY", font=font_title, fill="white")
        y = 138

        def wrap(value, font, max_width):
            text = str(value) if value is not None else ""
            # Character-based wrapping handles Thai text without spaces.
            lines, current = [], ""
            for ch in text:
                candidate = current + ch
                if draw.textlength(candidate, font=font) > max_width and current:
                    lines.append(current)
                    current = ch
                else:
                    current = candidate
            lines.append(current)
            return lines

        for section_title, headers, rows in sections:
            draw.rounded_rectangle((margin, y, width-margin, y+52), radius=9, fill="#FCE8E8")
            draw.text((margin+15, y+9), section_title, font=font_head, fill=red)
            y += 65
            count = len(headers)
            if count == 2:
                ratios = [0.35, 0.65]
            elif count == 4:
                ratios = [0.20, 0.10, 0.09, 0.61]
            else:
                ratios = [1/count]*count
            usable = width-2*margin
            bounds = [margin]
            for ratio in ratios:
                bounds.append(bounds[-1]+usable*ratio)
            row_data = [headers]+list(rows)
            for idx, record in enumerate(row_data):
                font = font_small if count > 5 else font_body
                wrapped = [wrap(v, font, max(30,bounds[j+1]-bounds[j]-24)) for j,v in enumerate(record)]
                line_h = 27 if count <= 5 else 24
                row_h = max(39, max(len(lines) for lines in wrapped)*line_h+16)
                draw.rectangle((margin,y,width-margin,y+row_h),fill=navy if idx==0 else ("#F3F6FA" if idx%2==0 else "#FFFFFF"))
                for j, lines in enumerate(wrapped):
                    x=bounds[j]+10
                    for k,line in enumerate(lines):
                        draw.text((x,y+7+k*line_h),line,font=font,fill="white" if idx==0 else navy)
                draw.line((margin,y+row_h,width-margin,y+row_h),fill="#DCE3EB",width=2)
                y += row_h
            y += 30
        note="Preliminary design only | Verify manufacturer specifications, airflow, heat loss and installation dimensions."
        draw.text((margin,y),note,font=font_small,fill=gray)
        y += 60
        cropped=image.crop((0,0,width,y))
        buffer=io.BytesIO()
        cropped.save(buffer,format="JPEG",quality=93,optimize=True,subsampling=0)
        return buffer.getvalue()

    def make_excel():
        wb = Workbook()
        sh = wb.active
        sh.title = "Summary"
        sh.merge_cells("A1:D1")
        sh["A1"] = "KSP | Farm Engineering — Summary"
        sh["A1"].font = Font(name="Arial", size=18, bold=True, color="FFFFFF")
        sh["A1"].fill = PatternFill("solid", fgColor="183153")
        sh["A1"].alignment = Alignment(vertical="center")
        sh.row_dimensions[1].height = 38
        row = 3
        def section(title, headers, data):
            nonlocal row
            n = len(headers)
            sh.merge_cells(start_row=row,start_column=1,end_row=row,end_column=n)
            c = sh.cell(row,1,title)
            c.fill=PatternFill("solid",fgColor="FCE8E8")
            c.font=Font(bold=True,color="B91C1C",size=12)
            sh.row_dimensions[row].height=27
            row+=1
            for col,label in enumerate(headers,1):
                c=sh.cell(row,col,str(label))
                c.fill=PatternFill("solid",fgColor="E8EDF4")
                c.font=Font(bold=True,color="183153")
                c.alignment=Alignment(wrap_text=True,vertical="center")
            sh.row_dimensions[row].height=32
            row+=1
            for record in data:
                for col,value in enumerate(record,1):
                    c=sh.cell(row,col,value if isinstance(value,(int,float)) else str(value) if value is not None else "")
                    c.alignment=Alignment(wrap_text=True,vertical="top")
                    if row%2==0:
                        c.fill=PatternFill("solid",fgColor="F3F6FA")
                sh.row_dimensions[row].height=45 if n<=4 else 55
                row+=1
            row+=2
        section("01 HOUSE DIMENSIONS",["Parameter","Value"],house_rows)
        section("02 EQUIPMENT SCHEDULE",["Equipment","Qty","Unit","Specification"], export_equipment)
        if export_detail:
            section("03 PAD / PUMP / AIR STEP BY SIDE", export_detail_headers, export_detail)
        section("04 CALCULATION DETAILS",["Parameter","Details"],calc_rows)
        for col in range(1,max(5,len(export_detail_headers)+1 if export_detail else 5)):
            sh.column_dimensions[get_column_letter(col)].width = 24 if col!=4 else 65
        sh.freeze_panes="A4"
        sh.sheet_view.showGridLines=False
        buf=io.BytesIO()
        wb.save(buf)
        return buf.getvalue()

    st.subheader("📥 ดาวน์โหลด Summary")
    st.caption("JPG และ Excel ใช้ข้อมูลเดียวกับหน้า Summary โดยจัดหน้ารายงานให้อ่านง่าย")
    export_signature = repr((width_m, height_m, house_length, air_speed_fpm, fan_cfm,
                             pad_height, pad_width, pad_face_velocity, layout, front_length,
                             heater_kw, factor, safety_margin, inlet_percent, conversion,
                             inlet_capacity, opening_ratio))
    if st.session_state.get("summary_export_signature") != export_signature:
        st.session_state.pop("summary_jpg", None)
        st.session_state.pop("summary_xlsx", None)
        st.session_state["summary_export_signature"] = export_signature
    if st.button("เตรียมไฟล์ JPG และ Excel", disabled=not sum_valid):
        errors = []
        try:
            st.session_state["summary_jpg"] = make_jpg()
        except Exception as exc:
            errors.append(f"JPG: {exc}")
        try:
            st.session_state["summary_xlsx"] = make_excel()
        except Exception as exc:
            errors.append(f"Excel: {exc}")
        if errors:
            for error in errors:
                st.error(f"ไม่สามารถสร้างไฟล์ {error}")
        else:
            st.success("เตรียมไฟล์ JPG และ Excel เรียบร้อยแล้ว")
    col_jpg, col_excel = st.columns(2)
    with col_jpg:
        if "summary_jpg" in st.session_state:
            st.download_button("🖼️ ดาวน์โหลด JPG",st.session_state["summary_jpg"],
                file_name="KSP_Farm_Engineering_Summary.jpg",mime="image/jpeg")
    with col_excel:
        if "summary_xlsx" in st.session_state:
            st.download_button("📊 ดาวน์โหลด Excel",st.session_state["summary_xlsx"],
                file_name="KSP_Farm_Engineering_Summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.warning('Summary เป็นรายการประมาณการเบื้องต้น ไม่ใช่ BOM เพื่อสั่งซื้อหรือแบบติดตั้งที่ผ่านการรับรอง ต้องตรวจสอบสเปกจริงและการปัดจำนวนแยกแต่ละด้านก่อนใช้งาน')
