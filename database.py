from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./lego_collection.db"

# the engine that drives the data to the file
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# local session, temp workplace, before "Save"
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# the base, the parent case where all future tables will use
Base = declarative_base()