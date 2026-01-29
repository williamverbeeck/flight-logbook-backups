import os
import streamlit as st
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from models import Base

def get_database_url():
    if "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    return "sqlite:///data/logbook.db"

DATABASE_URL = get_database_url()

connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args = {"sslmode": "require"}
elif DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔐 AUTOMATISCHE, EENMALIGE INIT
def _auto_init_db():
    inspector = inspect(engine)
    if not inspector.has_table("flights"):
        Base.metadata.create_all(bind=engine)

_auto_init_db()
