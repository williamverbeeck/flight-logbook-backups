from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///data/logbook.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)