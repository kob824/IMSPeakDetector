import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, BLOB, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_FILE = './db/ims.db'
engine = create_engine(f'sqlite:///{DB_FILE}')
Base = declarative_base()

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

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def select_columns_from_db(columns, table='measurements'):
    """
    Select columns from the specified table.
    
    Parameters:
    - columns: List of column names
    - table: Table name (default: 'measurements')
    
    Returns:
    - DataFrame with selected data
    """
    if table == 'measurements':
        query = session.query(*[getattr(Measurement, col) for col in columns])
        results = query.all()
        df = pd.DataFrame(results, columns=columns)
    else:
        # For other tables, use raw SQL
        columns_str = ', '.join(columns)
        query = f"SELECT {columns_str} FROM {table}"
        df = pd.read_sql_query(query, engine)
    
    return df

def load_csv_and_insert(csv_file):
    df = pd.read_csv(csv_file, header=0)
    print("DataFrame head:")
    print(df.head())
    
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

def get_substance_library():
    """
    Retrieve the substance library with K0 values from the database.
    """
    columns = ["id", "substance_name", 
               "k0_pos_1", "k0_pos_2", "k0_pos_3", 
               "k0_neg_1", "k0_neg_2", "k0_neg_3"]
    
    return select_columns_from_db(columns, table='library')