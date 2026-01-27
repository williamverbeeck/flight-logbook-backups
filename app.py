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

    x_margin = 40
    y = height - 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Personal Flight Logbook")
    y -= 30

    c.setFont("Helvetica", 8)

    for _, row in df.iterrows():
        line = (
            f"{row['Date']} | "
            f"{row['Aircraft']} | "
            f"{row['From']} → {row['To']} | "
            f"{row['Flight Time']} h"
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

        # 🗓️ Flight date
        flight_date = st.date_input("Flight Date", date.today())

        st.markdown("### Route & Timing")

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

        # ⏱ Block times
        col_bt1, col_bt2 = st.columns(2)
        block_off = col_bt1.time_input("Block Off")
        block_on = col_bt2.time_input("Block On")

        st.markdown("### Aircraft")

        col_a1, col_a2 = st.columns(2)
        aircraft_type = col_a1.text_input("Aircraft Type (e.g. C172)")
        registration = col_a2.text_input("Registration")

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

        flight_type = st.selectbox(
            "Flight Type",
            ["VFR", "IFR", "Y (IFR → VFR)", "Z (VFR → IFR)", "Z2 (VFR → IFR → VFR)"]
        )

        st.markdown("### Approaches & Landings")

        approach_type = st.selectbox(
            "Approach Type",
            [
                "None",
                "Visual",
                "ASR/SRA",
                "LOC",
                "LDA",
                "LNAV",
                "LP",
                "NDB",
                "VDF",
                "VOR",
                "TACAN",
                "Circling",
                "Sidestep",
                "PAR",
                "LNAV/VNAV",
                "LPV",
                "ILS CAT I",
                "ILS CAT II",
                "ILS CAT III",
                "MLS CAT I",
                "MLS CAT II",
                "MLS CAT III",
                "GLS CAT I",
                "RNP0.X"
            ]
        )

        col_l1, col_l2, col_l3 = st.columns(3)
        landings_day = col_l1.number_input("Day Landings", min_value=0, step=1)
        landings_night = col_l2.number_input("Night Landings", min_value=0, step=1)
        approach_count = col_l3.number_input("Approach Count", min_value=0, step=1)

        remarks = st.text_area("Remarks")

        submitted = st.form_submit_button("Save Flight")

        if submitted:
            # ⏱ Block time calculation
            block_minutes = (
                datetime.combine(date.today(), block_on)
                - datetime.combine(date.today(), block_off)
            ).total_seconds() / 60

            block_time = round(block_minutes / 60, 2)

            # Automatic time attribution
            pic_time = block_time if pilot_function in ["PIC", "Student PIC", "PIC under supervision"] else 0
            dual_time = block_time if pilot_function == "DUAL" else 0

            session = SessionLocal()
            flight = Flight(
                date=flight_date,

                departure=departure,
                arrival=arrival,
                dep_time=dep_time,
                arr_time=arr_time,

                block_off=block_off,
                block_on=block_on,
                block_time=block_time,

                aircraft_type=aircraft_type,
                registration=registration,

                pilot_function=pilot_function,
                flight_type=flight_type,

                approach_type=approach_type,
                approach_count=approach_count,

                flight_time=block_time,
                pic_time=pic_time,
                dual_time=dual_time,

                landings_day=landings_day,
                landings_night=landings_night,

                remarks=remarks
            )

            session.add(flight)
            session.commit()
            session.close()

            st.success("Flight saved ✈️")


if page == "Logbook":
    st.header("Flight Logbook")

    session = SessionLocal()
    flights = session.query(Flight).order_by(Flight.date.desc()).all()
    session.close()

    if not flights:
        st.info("No flights logged yet.")
    else:
        data = []
        for f in flights:
            data.append({
                "Date": f.date,
                "From": f.departure,
                "To": f.arrival,
                "Aircraft": f.aircraft_type,
                "Reg": f.registration,
                "Block Time": f.block_time,
                "Function": f.pilot_function,
                "PIC": f.pic_time,
                "Dual": f.dual_time,
                "Day Ldg": f.landings_day,
                "Night Ldg": f.landings_night,
                "Remarks": f.remarks
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📤 Export CSV",
            data=csv_data,
            file_name="flight_logbook.csv",
            mime="text/csv"
        )

        if st.button("📄 Export PDF"):
            pdf_path = export_logbook_pdf(df)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=f,
                    file_name="flight_logbook.pdf",
                    mime="application/pdf"
        )

        st.subheader("Totals")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Flight Time", f"{df['Flight Time'].sum():.1f} h")
        col2.metric("Total PIC", f"{df['PIC'].sum():.1f} h")
        col3.metric("Total Dual", f"{df['Dual'].sum():.1f} h")

st.sidebar.markdown("---")
if st.sidebar.button("Backup Logbook"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy(
        "data/logbook.db",
        f"backups/logbook_{timestamp}.db"
    )
    st.sidebar.success("Backup created")