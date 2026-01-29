import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from models import Base

def get_database_url():
    # 1️⃣ Streamlit secrets
    if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]

    # 2️⃣ Environment variable
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")

    # 3️⃣ Safe local default
    return "sqlite:///data/logbook.db"


DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)