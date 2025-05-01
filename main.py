from modules import sqlite_helper
import numpy as np
from scipy.signal import savgol_filter, find_peaks
import matplotlib.pyplot as plt  # Add this import

def process_spectrum(spectrum):
    spectrum = np.fromstring(spectrum[2:-1], sep=', ')  # Convert byte string to numpy array
    
    smoothed_spectrum = savgol_filter(spectrum, window_length=11, polyorder=3, deriv=2)
    
    peaks, properties = find_peaks(smoothed_spectrum, height=0)
    
    top_peaks = sorted(zip(peaks, properties['peak_heights']), key=lambda x: x[1], reverse=True)[:10]
    
    return [(int(idx), float(height)) for idx, height in top_peaks]

def plot_spectrum(spectrum, peaks):
    """
    Plots the spectrum and highlights the detected peaks.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(spectrum, label="Spectrum")
    plt.scatter(peaks, [spectrum[p] for p in peaks], color='red', label="Peaks")
    plt.title("Spectrum with Detected Peaks")
    plt.xlabel("Index")
    plt.ylabel("Intensity")
    plt.legend()
    plt.show()

def main():
    csv_file = r"./data/test.csv"
    # # sqlite_helper.load_csv_and_insert(csv_file)

    df = sqlite_helper.select_columns_from_db(["measurement_time", "pos_spectrum"])
    
    for index, row in df.iterrows():
        measurement_time = row["measurement_time"]
        pos_spectrum = row["pos_spectrum"]

        spectrum = np.fromstring(pos_spectrum[2:-1], sep=', ')
        
        if np.all(spectrum == 0):
            print(f"Skipping spectrum at Measurement Time: {measurement_time} (contains only zeros)")
            continue
        
        top_peaks = process_spectrum(pos_spectrum)
        peak_indices = [idx for idx, _ in top_peaks]
        
        plot_spectrum(spectrum, peak_indices)
        
        print(f"Measurement Time: {measurement_time}")
        print(f"Top 10 Peaks: {top_peaks}")

if __name__ == "__main__":
    main()