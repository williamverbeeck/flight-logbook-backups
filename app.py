import streamlit as st
from datetime import date
from database import SessionLocal
from models import Flight
import pandas as pd
import shutil
from datetime import datetime

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
        flight_date = st.date_input("Date", date.today())

        col1, col2 = st.columns(2)
        aircraft_type = col1.text_input("Aircraft Type (e.g. C172)")
        registration = col2.text_input("Registration")

        col3, col4 = st.columns(2)
        departure = col3.text_input("Departure")
        arrival = col4.text_input("Arrival")

        col5, col6, col7 = st.columns(3)
        flight_time = col5.number_input("Flight Time (h)", min_value=0.0, step=0.1)
        pic_time = col6.number_input("PIC Time (h)", min_value=0.0, step=0.1)
        dual_time = col7.number_input("Dual Time (h)", min_value=0.0, step=0.1)

        col8, col9 = st.columns(2)
        landings_day = col8.number_input("Day Landings", min_value=0, step=1)
        landings_night = col9.number_input("Night Landings", min_value=0, step=1)

        remarks = st.text_area("Remarks")

        submitted = st.form_submit_button("Save Flight")

        if submitted:
            session = SessionLocal()
            flight = Flight(
                date=flight_date,
                aircraft_type=aircraft_type,
                registration=registration,
                departure=departure,
                arrival=arrival,
                flight_time=flight_time,
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
                "Aircraft": f.aircraft_type,
                "Reg": f.registration,
                "From": f.departure,
                "To": f.arrival,
                "Flight Time": f.flight_time,
                "PIC": f.pic_time,
                "Dual": f.dual_time,
                "Day Ldg": f.landings_day,
                "Night Ldg": f.landings_night,
                "Remarks": f.remarks
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

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
