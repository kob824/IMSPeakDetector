import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the SQLite database file path
DB_FILE = './db/ims.db'
engine = create_engine(f'sqlite:///{DB_FILE}')
Base = declarative_base()

# Define the Measurement model
class Measurement(Base):
    __tablename__ = 'measurements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    measurement_time = Column(String)
    channel_1 = Column(Float)
    channel_2 = Column(Float)
    channel_3 = Column(Float)
    channel_4 = Column(Float)
    channel_5 = Column(Float)
    channel_6 = Column(Float)
    channel_7 = Column(Float)
    channel_8 = Column(Float)
    dilution = Column(Float)
    temperature_drift_tube = Column(Float)
    pressure = Column(Float)
    pos_voltage = Column(Float)
    neg_voltage = Column(Float)
    tube_length = Column(Float)
    pressure_offset = Column(Float)
    pressure_gradient = Column(Float)
    pos_spectrum = Column(BLOB)
    neg_spectrum = Column(BLOB)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)

# Set up the session
Session = sessionmaker(bind=engine)
session = Session()

# Function to select particular columns from the database
def select_columns_from_db(columns):
    # Query the database for the specified columns
    query = session.query(*[getattr(Measurement, col) for col in columns])
    results = query.all()
    
    # Convert the results to a DataFrame
    df = pd.DataFrame(results, columns=columns)
    return df

def load_csv_and_insert(csv_file):
    # Read CSV with header row
    df = pd.read_csv(csv_file, header=0)
    print("DataFrame head:")
    print(df.head())
    
    # Iterate over each row and create a Measurement record
    for index, row in df.iterrows():
        try:
            measurement = Measurement(
                measurement_time = row["measurement_time"],
                channel_1 = float(row["channel_1"]),
                channel_2 = float(row["channel_2"]),
                channel_3 = float(row["channel_3"]),
                channel_4 = float(row["channel_4"]),
                channel_5 = float(row["channel_5"]),
                channel_6 = float(row["channel_6"]),
                channel_7 = float(row["channel_7"]),
                channel_8 = float(row["channel_8"]),
                dilution = float(row["dilution"]),
                temperature_drift_tube = float(row["temperature_drift_tube"]),
                pressure = float(row["pressure"]),
                pos_voltage = float(row["pos_voltage"]),
                neg_voltage = float(row["neg_voltage"]),
                tube_length = float(row["tube_length"]),
                pressure_offset = float(row["press_offset"]),
                pressure_gradient = float(row["press_gradient"]),
                pos_spectrum = row["pos_spectrum"].encode('utf-8'),
                neg_spectrum = row["neg_spectrum"].encode('utf-8')
            )
            session.add(measurement)
        except ValueError as ve:
            print(f"Error converting row {index}: {ve}")
    
    session.commit()
    print(f"Inserted {len(df)} records into the database.")

    