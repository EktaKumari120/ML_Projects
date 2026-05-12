from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date

# Base is the parent class all the models will inherit from
Base = declarative_base()

# "table" defined as a Python class
class Transaction(Base):
    __tablename__ = "transactions"   # name of the table in SQLite

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)   # Food, Rent, Salary, etc.
    type = Column(String, nullable=False)        # "income" or "expense"
    description = Column(String, default="")
    date = Column(Date, default=date.today)

# create_engine : connects Python to SQLite file
engine = create_engine("sqlite:///finance.db", echo=False)

# This creates the actual table in the database if it doesn't exist yet
Base.metadata.create_all(engine)

# Session is what you use to talk to the database (add, query, delete)
SessionLocal = sessionmaker(bind=engine)
