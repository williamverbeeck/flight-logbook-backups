from sqlalchemy import Column, Integer, String, Float, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True)
    date = Column(Date)

    # Aircraft & route
    aircraft_type = Column(String)
    registration = Column(String)
    departure = Column(String)
    arrival = Column(String)

    # ⏱ NEW – Block timing (zoals EASA)
    block_off = Column(Time)
    block_on = Column(Time)
    block_time = Column(Float)   # in hours

    # 🧑‍✈️ NEW – Pilot function
    pilot_function = Column(String)  # PIC / DUAL / COP / INSTR

    # Existing (houden we)
    flight_time = Column(Float)
    pic_time = Column(Float)
    dual_time = Column(Float)

    landings_day = Column(Integer)
    landings_night = Column(Integer)
    remarks = Column(String)

    # Route timing (uitgebreid)
    dep_time = Column(Time)
    arr_time = Column(Time)

    # Pilot & operation
    pilot_function = Column(String)
    flight_type = Column(String)        # VFR / IFR / Y / Z / Z2
    approach_type = Column(String)
    approach_count = Column(Integer)