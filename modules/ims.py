import numpy as np
from scipy.signal import savgol_filter, find_peaks
import matplotlib.pyplot as plt

def process_spectrum(spectrum):
    spectrum = np.fromstring(spectrum[2:-1], sep=', ')

    smoothed_spectrum = savgol_filter(spectrum, window_length=11, polyorder=3)
    
    peaks, properties = find_peaks(smoothed_spectrum, height=np.max(smoothed_spectrum) * 0.1, distance=5)
    
    top_peaks = sorted(zip(peaks, properties['peak_heights']), key=lambda x: x[1], reverse=True)[:10]
    
    return [(int(idx), float(height)) for idx, height in top_peaks]

def calculate_k0_value(peaks, temperature, pressure, voltage, drift_tube_length, resolution):
    """
    Calculate the k0 value based on the peaks, temperature, pressure, drift tube length, and resolution.
    Returns a list of K0 values for each peak.

    The formulas needed are as follows:
    drift_time = (peak_position + position_offset) * (resolution / 1000000)
    k = length_squared / (drift_time * voltage)
    k0 = k * (nominal_temperature / temperature) * (pressure / nominal_pressure)  
    """
    nominal_temperature = 273.15  # Kelvin
    nominal_pressure = 1013.25  # kPa
    position_offset = 31 + 1
    length_squared = drift_tube_length ** 2
    temperature = temperature + 273.15  # Convert to Kelvin

    k0_values = []
    for peak in peaks:
        peak_position = peak[0]  # Peak index
        drift_time = (peak_position + position_offset) * (resolution / 1000000)  # Drift time in seconds
        k = length_squared / (drift_time * voltage)  
        k0 = k * (nominal_temperature / temperature) * (pressure / nominal_pressure) 
        k0_values.append(k0)

    return k0_values