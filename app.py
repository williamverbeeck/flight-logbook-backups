import streamlit as st
from datetime import date
from database import SessionLocal
from models import Flight
import pandas as pd
import shutil
from datetime import datetime
import subprocess
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

PASSWORD = st.secrets["APP_PASSWORD"]
pw = st.text_input("Password", type="password")
if pw != PASSWORD:
    st.error("Incorrect password")
    st.stop()

def auto_backup_and_push():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/logbook_{timestamp}.db"

    # 1. Maak backup
    shutil.copy("data/logbook.db", backup_file)

    # 2. Git add / commit / push
    subprocess.run(["git", "add", "backups"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["git", "commit", "-m", f"Auto backup {timestamp}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    subprocess.run(
        ["git", "push"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
if "auto_backup_done" not in st.session_state:
    try:
        auto_backup_and_push()
        st.session_state.auto_backup_done = True
    except Exception:
        st.session_state.auto_backup_done = True

def export_logbook_pdf(df):
    file_path = "flight_logbook.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    x_margin = 30
    y = height - 40

    # Titel
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "EASA Flight Logbook")
    y -= 25

    c.setFont("Helvetica", 8)

    for _, row in df.iterrows():
        line = (
            f"{row['DATE']} | "
            f"{row['DEP PLACE']} {row['DEP TIME']} → "
            f"{row['ARR PLACE']} {row['ARR TIME']} | "
            f"TT: {row['TOTAL FLIGHT TIME']} | "
            f"PIC: {row['PIC NAME']}"
        )

        c.drawString(x_margin, y, line)
        y -= 12

        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 8)
            y = height - 40

    c.save()
    return file_path


st.set_page_config(
    page_title="Flight Logbook",
    layout="wide"
)

st.title("✈️ Personal Flight Logbook")

page = st.sidebar.radio(
    "Navigation",
    ["Add Flight", "Logbook"]
)


if page == "Add Flight":
    st.header("Add New Flight")

    with st.form("flight_form"):

        st.markdown("### Route & Timing")
        
        # 🗓️ Flight date
        flight_date = st.date_input("Flight Date", date.today())

        col_left, col_right = st.columns(2)

        # ⬅️ Departure
        with col_left:
            st.subheader("Departure")
            departure = st.text_input("Departure Airport")
            dep_time = st.time_input("Departure Time")

        # ➡️ Arrival
        with col_right:
            st.subheader("Arrival")
            arrival = st.text_input("Arrival Airport")
            arr_time = st.time_input("Arrival Time")

        st.markdown("### Aircraft")

        col_a1, col_a2 = st.columns(2)
        aircraft_type = col_a1.text_input("Aircraft Type (e.g. C172)")
        registration = col_a2.text_input("Registration")
        is_single_engine = st.checkbox("Single Engine Aircraft")
        is_fstd = st.checkbox("Flight Training Simulation Device (FSTD / Simulator)")

        st.markdown("### Pilot & Operation")

        pilot_function = st.selectbox(
            "Pilot Function",
            [
                "PIC",
                "SIC",
                "DUAL",
                "Student PIC",
                "PIC under supervision",
                "Instructor",
                "Examiner",
                "Third Pilot",
                "Flight attendant",
                "Other"
            ]
        )

        pic_name = st.text_input("PIC Name")

        # flight_type = st.selectbox(
        #     "Flight Type",
        #     ["VFR", "IFR", "Y (IFR → VFR)", "Z (VFR → IFR)", "Z2 (VFR → IFR → VFR)"]
        # )

        st.markdown("### Landings")

        # approach_type = st.selectbox(
        #     "Approach Type",
        #     [
        #         "None",
        #         "Visual",
        #         "ASR/SRA",
        #         "LOC",
        #         "LDA",
        #         "LNAV",
        #         "LP",
        #         "NDB",
        #         "VDF",
        #         "VOR",
        #         "TACAN",
        #         "Circling",
        #         "Sidestep",
        #         "PAR",
        #         "LNAV/VNAV",
        #         "LPV",
        #         "ILS CAT I",
        #         "ILS CAT II",
        #         "ILS CAT III",
        #         "MLS CAT I",
        #         "MLS CAT II",
        #         "MLS CAT III",
        #         "GLS CAT I",
        #         "RNP0.X"
        #     ]
        # )

        col_l1, col_l2, col_l3 = st.columns(3)
        landings_day = col_l1.number_input("Day Landings", min_value=0, step=1)
        landings_night = col_l2.number_input("Night Landings", min_value=0, step=1)
        # approach_count = col_l3.number_input("Approach Count", min_value=0, step=1)

        st.markdown("### Operational Conditions Time")

        col_oc1, col_oc2 = st.columns(2)

        night_time = col_oc1.number_input(
            "Night (h)",
            min_value=0.0,
            step=0.1,
            help="Time flown under night conditions"
        )

        ifr_time = col_oc2.number_input(
            "IFR (h)",
            min_value=0.0,
            step=0.1,
            help="Time flown under IFR"
        )


        remarks = st.text_area("Remarks")

        submitted = st.form_submit_button("Save Flight")

        if submitted:
            # ⏱ Block time calculation
            block_minutes = (
                datetime.combine(date.today(), arr_time)
                - datetime.combine(date.today(), dep_time)
            ).total_seconds() / 60

            block_time = round(block_minutes / 60, 2)

            # Automatic time attribution
            pic_time = block_time if pilot_function in ["PIC", "Student PIC", "PIC under supervision"] else 0
            dual_time = block_time if pilot_function == "DUAL" else 0
            instr_time = block_time if pilot_function in ["Instructor", "Examiner"] else 0
            cop_time = block_time if pilot_function in ["SIC", "Third Pilot"] else 0

            # Multipilot determination (automatic)
            multi_pilot_roles = ["SIC", "PIC under supervision", "Third Pilot"]
            is_multi_pilot = pilot_function in multi_pilot_roles

            # Time allocation
            multi_pilot_time = block_time if is_multi_pilot else 0

            session = SessionLocal()
            flight = Flight(
                date=flight_date,

                departure=departure,
                arrival=arrival,
                dep_time=dep_time,
                arr_time=arr_time,

                block_time=block_time,

                aircraft_type=aircraft_type,
                registration=registration,

                pilot_function=pilot_function,
                # flight_type=flight_type,

                # approach_type=approach_type,
                # approach_count=approach_count,

                flight_time=block_time,
                pic_time=pic_time,
                cop_time=cop_time,
                dual_time=dual_time,
                instr_time=instr_time,
                pic_name=pic_name,
                is_fstd=is_fstd,

                is_single_engine=is_single_engine,
                is_multi_pilot=is_multi_pilot,
                multi_pilot_time=multi_pilot_time,

                landings_day=landings_day,
                landings_night=landings_night,

                night_time=night_time,
                ifr_time=ifr_time,

                remarks=remarks
            )

            session.add(flight)
            session.commit()
            session.close()

            st.success("Flight saved ✈️")


if page == "Logbook":
    
    st.header("EASA Flight Logbook")

    session = SessionLocal()
    flights = session.query(Flight).order_by(Flight.date.desc()).all()
    session.close()

    if not flights:
        st.info("No flights logged yet.")
    else:
        rows = []

        for f in flights:
            rows.append({
                # DATE
                "DATE": f.date.strftime("%d/%m/%Y") if f.date else "",

                # DEPARTURE
                "DEP PLACE": f.departure or "",
                "DEP TIME": f.dep_time.strftime("%H:%M") if f.dep_time else "",

                # ARRIVAL
                "ARR PLACE": f.arrival or "",
                "ARR TIME": f.arr_time.strftime("%H:%M") if f.arr_time else "",

                # AIRCRAFT
                "TYPE": f.aircraft_type or "",
                "REG": f.registration or "",

                # SINGLE / MULTI PILOT
                # OPERATION CATEGORY (EXACTLY ONE)
                "SE": "✓" if not f.is_multi_pilot and f.is_single_engine else "",
                "ME": "✓" if not f.is_multi_pilot and not f.is_single_engine else "",
                "MP": f.block_time if f.is_multi_pilot else "",


                # TOTAL TIME
                "TOTAL FLIGHT TIME": f"{f.block_time:.2f}" if f.block_time else "0.00",

                # PIC NAME
                "PIC NAME": f.pic_name or "SELF",

                # LANDINGS
                "LDG DAY": f.landings_day or 0,
                "LDG NIGHT": f.landings_night or 0,

                # OPERATIONAL CONDITIONS
                "NIGHT TIME": f.night_time or "",
                "IFR TIME": f.ifr_time or "",

                # PILOT FUNCTION TIME
                "PIC": f.pic_time or "",
                "COP": f.cop_time or "",
                "DUAL": f.dual_time or "",
                "INSTR": f.instr_time or "",

                # FSTD
                "FSTD TYPE": f.aircraft_type if f.is_fstd else "",
                "FSTD TIME": f"{f.block_time:.2f}" if f.is_fstd else "",


                # REMARKS
                "REMARKS AND ENDORSEMENTS": f.remarks or ""
            })

        df = pd.DataFrame(rows)

        # Display like a logbook, not like analytics
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Export Logbook")

        col_exp1, col_exp2 = st.columns(2)

        # ---------- CSV EXPORT ----------
        csv_data = df.to_csv(index=False).encode("utf-8")

        with col_exp1:
            st.download_button(
                label="📤 Export CSV",
                data=csv_data,
                file_name="flight_logbook.csv",
                mime="text/csv"
            )

        # ---------- PDF EXPORT ----------
        with col_exp2:
            if st.button("📄 Generate PDF"):
                pdf_path = export_logbook_pdf(df)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=f,
                        file_name="flight_logbook.pdf",
                        mime="application/pdf"
                    )


        # === TOTALS (OPTIONAL, BELOW TABLE) ===
        st.subheader("Totals")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Flight Time",
            f"{sum(f.block_time or 0 for f in flights):.2f} h"
        )

        col2.metric(
            "Total PIC",
            f"{sum(f.pic_time or 0 for f in flights):.2f} h"
        )

        col3.metric(
            "Total Dual",
            f"{sum(f.dual_time or 0 for f in flights):.2f} h"
        )


st.sidebar.markdown("---")
if st.sidebar.button("Backup Logbook"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(
        "data/logbook.db",
        f"backups/logbook_{timestamp}.db"
    )
    st.sidebar.success("Backup created")