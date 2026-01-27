from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    aircraft_type = Column(String)
    registration = Column(String)
    departure = Column(String)
    arrival = Column(String)
    flight_time = Column(Float)
    pic_time = Column(Float)
    dual_time = Column(Float)
    landings_day = Column(Integer)
    landings_night = Column(Integer)
    remarks = Column(String)
