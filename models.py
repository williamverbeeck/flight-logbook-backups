from sqlalchemy import Column, Integer, String, Float, Date, Time, Boolean
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

    # 🧑‍✈️ NEW – Pilot function
    is_single_engine = Column(Boolean)
    is_multi_pilot = Column(Boolean)
    multi_pilot_time = Column(Float)

    pilot_function = Column(String)  # PIC / DUAL / COP / INSTR
    flight_time = Column(Float)
    pic_time = Column(Float)
    cop_time = Column(Float)
    instr_time = Column(Float)  
    dual_time = Column(Float)

    block_time = Column(Float)

    landings_day = Column(Integer)
    landings_night = Column(Integer)
    remarks = Column(String)

    # Route timing (uitgebreid)
    dep_time = Column(Time)
    arr_time = Column(Time)

    night_time = Column(Float)
    ifr_time = Column(Float)

    # Pilot & operation
    pilot_function = Column(String)
    flight_type = Column(String)        # VFR / IFR / Y / Z / Z2
    approach_type = Column(String)
    approach_count = Column(Integer)

    pic_name = Column(String)
    is_fstd = Column(Boolean)