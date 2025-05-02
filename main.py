from modules import sqlite_helper
from modules.ims import process_spectrum, plot_spectrum, calculate_k0_value  # Import IMS functions
import numpy as np

def main():
    csv_file = r"./data/test.csv"
    # # sqlite_helper.load_csv_and_insert(csv_file)

    df = sqlite_helper.select_columns_from_db(["measurement_time", "pos_spectrum", "neg_spectrum", "temperature_drift_tube", "pressure", "pos_voltage", "neg_voltage", "tube_length"])

    count = 0
    
    for index, row in df.iterrows():
        measurement_time = row["measurement_time"]
        pos_spectrum = row["pos_spectrum"]
        neg_spectrum = row["neg_spectrum"]
        temperature = row["temperature_drift_tube"]
        pressure = row["pressure"]
        pos_voltage = row["pos_voltage"]
        neg_voltage = row["neg_voltage"]
        drift_tube_length = row["tube_length"]
        resolution = 32.392  

        pos_spectrum_array = np.fromstring(pos_spectrum[2:-1], sep=', ')
        neg_spectrum_array = np.fromstring(neg_spectrum[2:-1], sep=', ')
        
        if np.all(pos_spectrum_array == 0) and np.all(neg_spectrum_array == 0):
            print(f"Skipping spectrum at Measurement Time: {measurement_time} (contains only zeros)")
            continue
        
        if not np.all(pos_spectrum_array == 0):
            pos_top_peaks = process_spectrum(pos_spectrum)
            pos_peak_indices = [idx for idx, _ in pos_top_peaks]
            pos_k0_values = calculate_k0_value(pos_top_peaks, temperature, pressure, pos_voltage, drift_tube_length, resolution)
            print(f"Measurement Time: {measurement_time} (Positive Spectrum)")
            print(f"Top 10 Peaks: {pos_top_peaks}")
            print(f"K0 Values: {pos_k0_values}")
        
        if not np.all(neg_spectrum_array == 0):
            neg_top_peaks = process_spectrum(neg_spectrum)
            neg_peak_indices = [idx for idx, _ in neg_top_peaks]
            neg_k0_values = calculate_k0_value(neg_top_peaks, temperature, pressure, neg_voltage, drift_tube_length, resolution)
            print(f"Measurement Time: {measurement_time} (Negative Spectrum)")
            print(f"Top 10 Peaks: {neg_top_peaks}")
            print(f"K0 Values: {neg_k0_values}")

    # print(sqlite_helper.select_columns_from_db(["measurement_time", "dilution", "pressure"]))

if __name__ == "__main__":
    main()