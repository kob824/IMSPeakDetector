from modules import sqlite_helper
from modules.ims import process_spectrum, calculate_k0_value
from modules.substance_identifier import identify_substances, DEFAULT_K0_TOLERANCE
from modules.visualization import show_scrollable_plots
import numpy as np
import pandas as pd

# Constants
K0_TOLERANCE = 0.2  # The tolerance used specifically in this script

def main():
    # csv_file = r"./data/HCl 10ppm.csv"
    # sqlite_helper.load_csv_and_insert(csv_file)

    df = sqlite_helper.select_columns_from_db(["measurement_time", "pos_spectrum", "neg_spectrum", 
                                              "temperature_drift_tube", "pressure", "pos_voltage", 
                                              "neg_voltage", "tube_length"])
    
    # Most of the rows in the database have either positive or negative spectrum data, not both
    # We need to merge them based on the presence of data in either spectrum
    # Process and merge the data to combine appropriate positive and negative spectra
    merged_data = []
    i = 0
    while i < len(df):
        current_row = df.iloc[i].copy()
        pos_spectrum = current_row["pos_spectrum"]
        neg_spectrum = current_row["neg_spectrum"]
        
        pos_spectrum_array = np.fromstring(pos_spectrum[2:-1], sep=', ')
        neg_spectrum_array = np.fromstring(neg_spectrum[2:-1], sep=', ')
        
        # Case 1: Both spectra have data - no need to merge
        if not np.all(pos_spectrum_array == 0) and not np.all(neg_spectrum_array == 0):
            merged_data.append(current_row)
            i += 1
            continue
            
        # Case 2: Current row has positive spectrum but no negative spectrum
        if not np.all(pos_spectrum_array == 0) and np.all(neg_spectrum_array == 0):
            # Look ahead for a row with negative spectrum data
            next_neg_idx = -1
            for j in range(i+1, len(df)):
                next_neg_array = np.fromstring(df.iloc[j]["neg_spectrum"][2:-1], sep=', ')
                next_pos_array = np.fromstring(df.iloc[j]["pos_spectrum"][2:-1], sep=', ')
                
                # If we find a row with negative data and no positive data
                if not np.all(next_neg_array == 0) and np.all(next_pos_array == 0):
                    next_neg_idx = j
                    break
                    
            if next_neg_idx != -1:
                # Merge the data - keep metadata from current row with positive spectrum
                merged_row = current_row.copy()
                merged_row["neg_spectrum"] = df.iloc[next_neg_idx]["neg_spectrum"]
                merged_data.append(merged_row)
                i = next_neg_idx + 1  # Skip to after the last used row
            else:
                # No matching negative spectrum found
                i += 1
            continue
            
        # Case 3: Current row has negative spectrum but no positive spectrum
        if np.all(pos_spectrum_array == 0) and not np.all(neg_spectrum_array == 0):
            # Look behind for the most recent row with positive spectrum data
            prev_pos_idx = -1
            for j in range(i-1, -1, -1):
                prev_pos_array = np.fromstring(df.iloc[j]["pos_spectrum"][2:-1], sep=', ')
                
                # If we find a row with positive data
                if not np.all(prev_pos_array == 0):
                    prev_pos_idx = j
                    break
                    
            if prev_pos_idx != -1:
                # We've already processed this by looking ahead from the positive spectrum row
                i += 1
            else:
                # No matching positive spectrum found before this
                i += 1
            continue
            
        # Case 4: Both spectra are empty
        i += 1

    visualization_data = []
    
    for i, row in enumerate(merged_data):
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
        
        # Skip if either spectrum is empty
        if np.all(pos_spectrum_array == 0) or np.all(neg_spectrum_array == 0):
            print(f"Skipping spectrum at Measurement Time: {measurement_time} (contains zeros in one spectrum)")
            continue
        
        print(f"\nProcessing Measurement Time: {measurement_time} (Entry {i+1}/{len(merged_data)})")
        
        pos_top_peaks = []
        pos_k0_values = []
        if not np.all(pos_spectrum_array == 0):
            pos_top_peaks = process_spectrum(pos_spectrum)
            pos_k0_values = calculate_k0_value(pos_top_peaks, temperature, pressure, pos_voltage, drift_tube_length, resolution)
            print(f"Positive Spectrum:")
            print(f"Top 10 Peaks: {pos_top_peaks}")
            print(f"K0 Values: {pos_k0_values}")
        
        neg_top_peaks = []
        neg_k0_values = []
        if not np.all(neg_spectrum_array == 0):
            neg_top_peaks = process_spectrum(neg_spectrum)
            neg_k0_values = calculate_k0_value(neg_top_peaks, temperature, pressure, neg_voltage, drift_tube_length, resolution)
            print(f"Negative Spectrum:")
            print(f"Top 10 Peaks: {neg_top_peaks}")
            print(f"K0 Values: {neg_k0_values}")
        
        # Identify substances based on K0 values
        # identified_substances = identify_substances(pos_k0_values, neg_k0_values, tolerance=0.02)
        identified_substances = identify_substances(pos_k0_values, neg_k0_values, tolerance=K0_TOLERANCE)
        
        if identified_substances:
            print(f"\nIdentified Substances:")
            for substance in identified_substances:
                print(f"- {substance['name']}")
                if substance['pos_matches']:
                    print(f"  Positive spectrum matches:")
                    for match in substance['pos_matches']:
                        print(f"    {match[0]} library value: {match[2]:.3f}, measured: {match[1]:.3f}")
                if substance['neg_matches']:
                    print(f"  Negative spectrum matches:")
                    for match in substance['neg_matches']:
                        print(f"    {match[0]} library value: {match[2]:.3f}, measured: {match[1]:.3f}")
        else:
            print("\nNo substances identified in this spectrum.")
        
        print("="*50)
        
        # data for visualization
        visualization_data.append({
            'measurement_time': measurement_time,
            'spectrums': {
                'pos': pos_spectrum_array,
                'neg': neg_spectrum_array
            },
            'peaks_data': {
                'pos': pos_top_peaks,
                'neg': neg_top_peaks,
                'pos_k0s': pos_k0_values,
                'neg_k0s': neg_k0_values
            },
            'identified_substances': identified_substances
        })

    print(f"\nFound {len(visualization_data)} complete spectra (with both positive and negative data)")
    print (f"\nTotal matches found: {sum(len(data['identified_substances']) for data in visualization_data)}")

    show_scrollable_plots(visualization_data)

if __name__ == "__main__":
    main()